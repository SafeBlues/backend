# dumb stuff
pushd ~/sb-aws/src
./generate_protos.sh
cp sb.pb ~/sb-aws/envoy
popd

pushd ~/sb-aws/proxy
docker build -t safeblues/envoy .
docker run -p 127.0.0.1:9901:9901 -p 443:4443 safeblues/envoy
popd
