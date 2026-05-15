FROM alpine:3.22
RUN apk add --no-cache python3 py3-pip build-base freetype-dev python3-dev git fastfetch
RUN pip3 install --no-cache-dir --break-system-packages matplotlib numpy ipykernel
EXPOSE 3000
CMD ["bash"]