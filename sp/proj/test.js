import http from 'k6/http';
import { sleep } from 'k6';
import { SharedArray } from 'k6/data';
import { scenario } from 'k6/execution';
import { vu } from 'k6/execution';
import { check } from 'k6';

const base_url = "https://pytlak.eu-central-1.elasticbeanstalk.com";
const files_endpoint = base_url + "/api/device/files?apiToken=";
const tasks_endpoint = base_url + "/api/device/tasks?apiToken=";

// device synchronization happens every 9-11 minutes
//const base_period = 9 * 60; // 9 minutes
//const random_period = 2 * 60; // 2 minutes
const base_period = 1; // 9 minutes
const random_period = 1; // 2 minutes


// not using SharedArray here will mean that the code in the function call (that is what loads and

// parses the json) will be executed per each VU which also means that there will be a complete copy

// per each VU

const data = new SharedArray('some data name', function () {

  return JSON.parse(open('./data/api_keys_2.json'));

});

export const options = {
    stages: [
        { duration: '10s', target: 200 },
        { duration: '10s', target: 500 },
        { duration: '10s', target: 800 },
        { duration: '10s', target: 1000 },
        { duration: '20s', target: 80 },
        { duration: '5s', target: 20 },
        { duration: '5s', target: 0 },
  ],
};


function check_response(response) {
    check(response, {
       'is status 200': (r) => r.status === 200,
    });
    if (response.status !== 200) {
        console.error(response.status);
    }
}

export default function() {
    const terminal = data[vu.idInTest % data.length];

    const a = http.get(files_endpoint + terminal.api_token);
    check_response(a);
    const b = http.get(tasks_endpoint + terminal.api_token);
    check_response(b);

    sleep(base_period + Math.random(random_period));
}
