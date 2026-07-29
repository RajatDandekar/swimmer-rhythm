import modal
app = modal.App("vesw-authtest")
@app.function(image=modal.Image.debian_slim().pip_install("numpy"))
def ping(x):
    import numpy as np
    return float(np.sqrt(x))
@app.local_entrypoint()
def main():
    print("parallel map result:", list(ping.map([4, 9, 16, 25])))
