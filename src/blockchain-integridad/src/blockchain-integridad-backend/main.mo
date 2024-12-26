import Blob "mo:base/Blob";
import Cycles "mo:base/ExperimentalCycles";
import Text "mo:base/Text";

import Types "types";

actor {

	// store in stable the http_response
    stable var stable_decoded_raw_text: Text = "";

    public query func transform(raw : Types.TransformArgs) : async Types.CanisterHttpResponsePayload {
        let transformed : Types.CanisterHttpResponsePayload = {
            status = raw.response.status;
            body = raw.response.body;
            headers = [
                {
                    name = "Content-Security-Policy";
                    value = "default-src 'self'";
                },
                { name = "Referrer-Policy"; value = "strict-origin" },
                { name = "Permissions-Policy"; value = "geolocation=(self)" },
                {
                    name = "Strict-Transport-Security";
                    value = "max-age=63072000";
                },
                { name = "X-Frame-Options"; value = "DENY" },
                { name = "X-Content-Type-Options"; value = "nosniff" },
            ];
        };
        transformed;
    };

    public func get_raw_data(url: Text) : async Text {
        let ic : Types.IC = actor ("aaaaa-aa");

        let request_headers = [
            { name = "Host"; value = "raw.githubusercontent.com" },
            { name = "User-Agent"; value = "lostigres" },
        ];

        let transform_context : Types.TransformContext = {
            function = transform;
            context = Blob.fromArray([]);
        };

        let http_request : Types.HttpRequestArgs = {
            url = url;
            max_response_bytes = null;
            headers = request_headers;
            body = null;
            method = #get;
            transform = ?transform_context;
        };

        Cycles.add(230_949_972_000);

        let http_response : Types.HttpResponsePayload = await ic.http_request(http_request);

        let response_body: Blob = Blob.fromArray(http_response.body);
        let decoded_text: Text = switch (Text.decodeUtf8(response_body)) {
            case (null) { "No value returned" };
            case (?y) { y };
        };

        stable_decoded_raw_text := decoded_text;

        decoded_text
    };

public query func get_stable_raw_json() : async Text {
    return stable_decoded_raw_text;
};

public func send_post_request(target_url: Text, user_input: Text) : async Text {
    let ic : Types.IC = actor ("aaaaa-aa");

    let request_headers = [
        { name = "Host"; value = "example.com" },
        { name = "User-Agent"; value = "lostigres-post" },
        { name = "Content-Type"; value = "application/json" },
    ];

    let request_body_as_blob: Blob = Text.encodeUtf8(user_input);
    let request_body_as_nat8: [Nat8] = Blob.toArray(request_body_as_blob);

    let http_request : Types.HttpRequestArgs = {
        url = target_url;
        max_response_bytes = null;
        headers = request_headers;
        body = ?request_body_as_nat8;
        method = #post;
        transform = null;
    };

    Cycles.add(230_949_972_000);

    let http_response : Types.HttpResponsePayload = await ic.http_request(http_request);

    let response_body: Blob = Blob.fromArray(http_response.body);
    let decoded_text: Text = switch (Text.decodeUtf8(response_body)) {
        case (null) { "No value returned" };
        case (?y) { y };
    };

    decoded_text
};

public query func compare_hashes(prev_hash: Text, new_hash: Text) : async Types.Result<Text, Text> {
    if (prev_hash == new_hash) { return #ok("Same document"); }
    else { return #err("Different documents"); };
};

};
