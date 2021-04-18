FROM envoyproxy/envoy:v1.15.0

COPY ./envoy.yaml /etc/envoy/envoy.yaml
COPY ./sb.pb /tmp/envoy/proto.pb

EXPOSE 8888
EXPOSE 9901

CMD /usr/local/bin/envoy -c /etc/envoy/envoy.yaml
