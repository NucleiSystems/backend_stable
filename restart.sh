git pull

systemctl restart nuclei_backend.service

journalctl -xe -u nuclei_backend.service -f --no-pager | awk '{gsub(/debian-s-1vcpu-1gb-intel-syd1-01/, ""); print}'
