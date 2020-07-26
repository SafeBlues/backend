protoc -I. --python_out=. -o sb.pb --grpc_python_out=. --plugin=protoc-gen-grpc_python=$(which grpc_python_plugin) sb.proto
