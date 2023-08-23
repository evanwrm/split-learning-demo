# Split Learning Demo

Simple implementation of split learning/split inference. A model is split at specified "cut" layer, and trained by a set of clients (holding input data), and a parameter server.

![Split Inference Web](https://github.com/evanwrm/split-learning-demo/assets/66049888/b79d461b-5178-4280-a5ba-4119e02bf7ff)

We provide a few example implementations based on the following scenarios:

| Type            | Network Communication | Client Framework | Server Framework |
| --------------- | --------------------- | ---------------- | ---------------- |
| Split Inference | Websockets            | Onnx Runtime     | PyTorch          |
| Split Learning  | Websockets            | PyTorch          | PyTorch          |
| Split Learning  | MPI                   | PyTorch          | PyTorch          |

## Installation

The core implementation is in Python (3.11). To install we can create a virtual environment using Conda:

```sh
conda create -f environment.yml
conda activate split-learning-demo
```

### Web

To install the webapp:

```sh
cd apps/web
pnpm install
```

## Usage

Demos scripts can be found in the `scripts` directory.

### Server/Client

To run a simple client/server split leraning setup:

```sh
python scripts/server.py --learning-rate=0.01
```

In a different terminal:

```sh
python scripts/client.py --learning-rate=0.01
```

### Server/Web

Make sure the webapp is installed (see above)

```sh
python scripts/server.py --learning-rate=0.01
```

In a different terminal:

```sh
cd apps/web
pnpm run dev
```

Navigate to `http://localhost:5173` in your browser. The websocket server will default to `ws://127.0.0.1:8000/ws`.

### MPI

To run the MPI demo with 1 server and 1 client:

```sh
mpirun -n 2 python scripts/mpi.py --leanring-rate=0.01
```

## TODO

-   [x] Add a simple local baseline model for comparisons
-   [x] Add split inference model
-   [ ] Introduce an adversarial attack
-   [ ] Add a serform a simple defence
-   [ ] Show and address SplitNN communication overheads with compression

## Citations

```bibtex
@article{vepakomma2018split,
    title={Split learning for health: Distributed deep learning without sharing raw patient data},
    author={Vepakomma, Praneeth and Gupta, Otkrist and Swedish, Tristan and Raskar, Ramesh},
    journal={arXiv preprint arXiv:1812.00564},
    year={2018}
}
```
