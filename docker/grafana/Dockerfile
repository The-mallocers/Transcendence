FROM grafana/grafana-enterprise

USER root
COPY ./volumes/grafana-init/create-api-token.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/create-api-token.sh

USER grafana