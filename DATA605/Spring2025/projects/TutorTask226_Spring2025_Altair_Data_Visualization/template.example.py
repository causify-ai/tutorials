import uvicorn

if __name__ == "__main__":
    uvicorn.run("template_API:app", host="127.0.0.1", port=8080, reload=True)
