FROM envoyproxy/envoy-dev:latest

COPY ./envoy.yaml /etc/envoy/envoy.yaml
COPY ./sb.pb /tmp/envoy/proto.pb
COPY certs /tmp/envoy/certs

EXPOSE 4443
EXPOSE 9901

CMD /usr/local/bin/envoy -c /etc/envoy/envoy.yaml
