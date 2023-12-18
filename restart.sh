git pull

systemctl restart nuclei_backend.service

journalctl -xe -u nuclei_backend.service -f