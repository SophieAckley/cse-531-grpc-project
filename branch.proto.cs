syntax = "proto3";

message MsgRequest {
	string interface = 1;
	int32 money = 2;
	repeated int32 writeset = 3;
}

message MsgResponse {
	string interface = 1;
	int32 money = 2;
	repeated int32 writeset = 3;
}

service Branch {
	rpc MsgDelivery(MsgRequest) returns (MsgResponse) {}
	rpc MsgPropagation(MsgRequest) returns (MsgResponse) {}
}