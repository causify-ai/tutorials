# Entry point for running the FastAPI app
import uvicorn

if __name__ == "__main__":
    uvicorn.run("Altair_API:app", host="127.0.0.1", port=8080, reload=True)
