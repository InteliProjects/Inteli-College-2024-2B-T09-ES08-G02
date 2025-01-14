module Types {

	// Error types

    public type ParseError = {
        message : Text;
    };

    public type Result<T, E> = {
        #ok : T;
        #err : E;
    };

	// Network types

    public type Timestamp = Nat64;

    public type HttpRequestArgs = {
        url : Text;
        max_response_bytes : ?Nat64;
        headers : [HttpHeader];
        body : ?[Nat8];
        method : HttpMethod;
        transform : ?TransformRawResponseFunction;
    };

    public type HttpHeader = {
        name : Text;
        value : Text;
    };

    public type HttpMethod = {
        #get;
        #post;
        #head;
    };

    public type HttpResponsePayload = {
        status : Nat;
        headers : [HttpHeader];
        body : [Nat8];
    };

    public type TransformRawResponseFunction = {
        function : shared query TransformArgs -> async HttpResponsePayload;
        context : Blob;
    };

    public type TransformArgs = {
        response : HttpResponsePayload;
        context : Blob;
    };

    public type CanisterHttpResponsePayload = {
        status : Nat;
        headers : [HttpHeader];
        body : [Nat8];
    };

    public type TransformContext = {
        function : shared query TransformArgs -> async HttpResponsePayload;
        context : Blob;
    };

    public type IC = actor {
        http_request : HttpRequestArgs -> async HttpResponsePayload;
    };

	// Type Example:

	public type DocumentRecord = {
		studytime: Nat;
		higher: Text;
		absences: Nat;
		failures: Text;
	};

	public type DocumentRecordS3 = {
  		s3_url: Text;
		s3_previous_url : Text;
		content : Text;
	}
};
