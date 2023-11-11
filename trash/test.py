server {
    server_name foodkilogram.hopto.org;

    location / {
    proxy_pass http://127.0.0.1:7000;
    proxy_set_header        Host $host;
    }


    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/foodkilogram.hopto.org/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/foodkilogram.hopto.org/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

}

server {
    if ($host = foodkilogram.hopto.org) {
        return 301 https://$host$request_uri;
    } # managed by Certbot

    server_name foodkilogram.hopto.org;
    server_tokens off;
    listen 80;
    return 404; # managed by Certbot
}




-----------------------------------------------------------------------------------
server {

    location / {
        proxy_pass http://127.0.0.1:8088;
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/foodkilogram.hopto.org/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/foodkilogram.hopto.org/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

}

server {
    if ($host = foodkilogram.hopto.org) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    listen 80;
    server_name 84.201.140.123 foodkilogram.hopto.org;
    return 404; # managed by Certbot


}



----------------------------------------------------------------------------------------
# build_and_push_in_to_docker_hub:
  #   name: Push Docker image to DockerHub
  #   runs-on: ubuntu-latest
  #   needs: tests
  #   steps:
  #     - name: Check out the repo
  #       uses: actions/checkout@v3

  #     - name: Set up Docker Buildx
  #       uses: docker/setup-buildx-action@v2

  #     - name: Login to Docker 
  #       uses: docker/login-action@v2
  #       with:
  #         username: ${{ secrets.DOCKER_USERNAME }} 
  #         password: ${{ secrets.DOCKER_PASSWORD }}

  #     - name: Push backend to DockerHub
  #       uses: docker/build-push-action@v4
  #       with:
  #         context: ./backend/
  #         push: true
  #         tags: ${{ secrets.DOCKER_USERNAME }}/foodgram_backend:latest

  #     - name: Push frontend to DockerHub
  #       uses: docker/build-push-action@v4
  #       with:
  #         context: ./frontend/
  #         push: true
  #         tags: ${{ secrets.DOCKER_USERNAME }}/foodgram_frontend:latest

  build_infra_and_push_to_docker_hub:
    name: Push infra Docker image to DockerHub
    runs-on: ubuntu-latest
    steps:
      - name: Check out the repo
        uses: actions/checkout@v3
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      - name: Login to Docker 
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      - name: Push to DockerHub
        uses: docker/build-push-action@v4
        with:
          context: ./infra/
          push: true
          tags: mralmostfreeman/foodgram_infra:latest