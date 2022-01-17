import http from 'k6/http';
import { sleep } from 'k6';
import { SharedArray } from 'k6/data';
import { vu } from 'k6/execution';
import { check } from 'k6';
import { status_endpoint_body } from "./status_endpoint_data.js";
import { uuid } from "./uuid.js";
import { get_save_tx_endpoint_data } from "./save_tx_endpoint_data.js";

const base_url = __ENV.PORTAL_BASE_URL;
const send_transactions = __ENV.SEND_TRANSACTIONS == "true";

// FILES endpoint (GET)
const files_endpoint = base_url + "/api/device/files?apiToken=";

// TASKS endpoints (GET)
const tasks_received_endpoint = base_url + "/api/device/tasks?status=RECEIVED&apiToken=";
const tasks_in_progress_endpoint = base_url + "/api/device/tasks?status=IN_PROGRESS&apiToken=";
const tasks_created_endpoint = base_url + "/api/device/tasks?status=CREATED&apiToken=";

// STATUS endpoint (PUT)
const status_endpoint = base_url + "/api/device/status?apiToken=";

// LAUNCHER app endpoint (GET)
const launcher_endpoint = base_url + "/api/apps/launcher?sn=";

// DEFAULT apps endpoint (GET)
const default_apps_endpoint = base_url + "/api/apps/list/default?apiToken=";

// mandatory apps endpoint (GET)
const mandatory_apps_endpoint = base_url + "/api/apps/list/mandatory?apiToken=";

// save transactions endpoint (POST)
const save_tx_endpoint = base_url + "/api/transactions?apiToken=";


// device synchronization happens every 9-11 minutes
const base_period = 9 * 60; // 9 minutes
const random_period = 2 * 60; // 2 minutes
const terminals_per_vu = 10;

// max transactions per terminal
const max_transactions_per_terminal = 4;


// not using SharedArray here will mean that the code in the function call (that is what loads and
// parses the json) will be executed per each VU which also means that there will be a complete copy
// per each VU
const data = new SharedArray('some data name', function () {
  return JSON.parse(open('./data/api_keys_3.json'));
});
const json_headers = { 'Content-Type': 'application/json' };

export const options = {
    discardResponseBodies: true,
    stages: [
        { duration: '660s', target: 1000 },
        { duration: '3600s', target: 1000 },
        { duration: '660s', target: 0 }
    ],
    thresholds: {
        http_req_failed: ['rate<0.01'], // http errors should be less than 1%
    }
};


function check_response(response, terminal) {
    check(response, {
       'is status 200': (r) => r.status >= 200 && r.status <= 299,
    });
    if (response.status < 200 || response.status > 299) {
        console.error(`For terminal=${terminal.id} got status code ${response.status} at ${response.request.url}`);
    }
}

export default function() {
    // Terminal synchronization behaviour is as following:
    // - check files
    // - check status
    // - check tasks CREATED
    // - check tasks RECEIVED
    // - check tasks IN_PROGRESS
    // - check apps Launcher
    // - check apps Default
    // - check apps Mandatory

    const sleep_time = base_period + Math.random() * random_period;

    const sleep_time_per_vu = sleep_time / terminals_per_vu;

    for (let i = 0; i < terminals_per_vu; i++) {
        let terminal_index = ((vu.idInTest - 1) * terminals_per_vu + i) % data.length;
        const terminal = data[terminal_index];

        // files request
        const files_response = http.get(files_endpoint + terminal.api_token);
        check_response(files_response, terminal);

        // terminal status request
        const status_response = http.put(status_endpoint + terminal.api_token, status_endpoint_body, { headers: json_headers });
        check_response(status_response, terminal);

        // tasks created
        const tasks_created_response = http.get(tasks_created_endpoint + terminal.api_token);
        check_response(tasks_created_response, terminal);

        // tasks received
        const tasks_received_response = http.get(tasks_received_endpoint + terminal.api_token);
        check_response(tasks_received_response, terminal);

        // tasks in_progress
        const tasks_in_progress_response = http.get(tasks_in_progress_endpoint + terminal.api_token);
        check_response(tasks_in_progress_response, terminal);

        // Launcher request
        const launcher_response = http.get(launcher_endpoint + terminal.serial_number);
        check_response(launcher_response, terminal);

        // default apps request
        const default_apps_response = http.get(default_apps_endpoint + terminal.api_token);
        check_response(default_apps_response, terminal);

        // default apps request
        const mandatory_apps_response = http.get(mandatory_apps_endpoint + terminal.api_token);
        check_response(mandatory_apps_response, terminal);

        if (send_transactions) {
            let transactions_to_be_sent = Math.random() * (max_transactions_per_terminal + 1);
            for (let j = 0; j < transactions_to_be_sent; j++) {
                // send a transaction with an unique UUID
                const data = get_save_tx_endpoint_data(uuid(), new Date());
                const save_tx_response = http.post(save_tx_endpoint + terminal.api_token, JSON.stringify(data), {
                    headers: json_headers
                });

                check_response(save_tx_response, terminal);

                sleep(sleep_time_per_vu / transactions_to_be_sent);
            }
        } else {
            sleep(sleep_time_per_vu);
        }
    }
}

