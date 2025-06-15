docker run -it --rm `
  -v ${PWD}:/app `
  -w /app `
  -p 8888:8888 `
  bitcoin-project `
  jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root
