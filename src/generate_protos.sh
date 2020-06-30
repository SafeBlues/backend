find . -name '*.proto' | protoc -I. --python_out=. --grpc_python_out=. --plugin=protoc-gen-grpc_python=$(which grpc_python_plugin) $(xargs)
