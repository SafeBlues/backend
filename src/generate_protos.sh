protoc -I. --include_imports -o sb.pb --python_out=. --grpc_python_out=. --plugin=protoc-gen-grpc_python=$(which grpc_python_plugin) sb.proto
cp sb.pb ../proxy/
