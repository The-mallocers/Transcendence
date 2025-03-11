FROM grafana/grafana-enterprise

# USER root

# RUN adduser --disabled-password bpoyet
# USER bpoyet

# # Create directories if they don't exist
# RUN mkdir -p /var/lib/grafana /etc/grafana/provisioning /grafana-init

# # Set permissions for the grafana user (UID 472)
# RUN chown -R bpoyet /var/lib/grafana /etc/grafana /grafana-init
# RUN chmod 777 /var/lib/grafana

# # Switch back to grafana user
# USER bpoyet

# FROM your-image
# USER root
# RUN mkdir -p /backup \
#  && chown -R your-user /backup
# USER your-user