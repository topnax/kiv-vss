import http from 'k6/http';
import { sleep } from 'k6';
import { check } from 'k6';

const base_url = __ENV.PORTAL_BASE_URL;


export const options = {
    discardResponseBodies: true,
    stages: [
        { duration: '60s', target: 1 },
        { duration: '60s', target: 1 },
        { duration: '0s', target: 0 }
    ],
    thresholds: {
        http_req_failed: ['rate<0.01'], // http errors should be less than 1%
    }
};


function get_apk_endpoint(package_name, name, version, api_token) {
    return `/api/apps/apk/${package_name}/${name}/${version}?apiToken=${api_token}`;
}

export default function() {
    // download an APK
    const apk_response = http.get(base_url + get_apk_endpoint("com.stpos.a8pos", "STPAY", "2.1.240", "5a7f416f-9d3c-4d7f-8a40-09515e310e48"));

    check(apk_response, {
      'status is 200': (r) => r.status === 200
    });
    sleep(1000);
}

