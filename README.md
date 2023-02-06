# uvicorn-issue-1862
DeflatePerMessage VS memory consumption MRE

# How to run server
`docker-compose up -d` will host uvicorn with default settings on `127.0.0.1:8000`

# Endpoints
* `/ws` - simple echo websocket from [here](https://fastapi.tiangolo.com/advanced/websockets/?h=websocket). 
  You can connect using `ws://127.0.0.1:8000/ws`  

* `GET /snapshot?limit=5` - returns [tracemalloc](https://docs.python.org/3/library/tracemalloc.html#traceback) snapshot:
```json
[
  {
    "count": 806,
    "bytes": 30854097,
    "traceback": [
      "  File \"/app/pip/lib/python3.8/site-packages/websockets/extensions/permessage_deflate.py\", line 64",
      "    self.encoder = zlib.compressobj("
    ]
  }
]
```

# Load generator
A simple python script generating websockets which do nothing (just wait for new messages).  
Usage: `python load_generator.py [ws_count]`.  
`ws_count` parameter is optional and defaults to `1000`.  


# How to test
1. Run server as written above
2. run load_generator.py 1000
3. Get `GET /snapshot` multiple times during socket generation. It will show that `zlib.compress()` allocates 
   more and more memory 