import json
from argparse import ArgumentParser
from sys import stderr
import sys
from typing import List, Tuple

import numpy as np

DEFAULT_N = 1000
OUT_FILE = "result.json"


def approx_pi(seed, n) -> Tuple[List[Tuple[float, float]], float]:
    rng = np.random.default_rng(seed)
    draws = rng.uniform(size=(2, n))
    pi_value = 4 * ((draws**2).sum(axis=0) <= 1).sum() / n
    return list(map(tuple, draws)), pi_value


def main() -> None:
    ap = ArgumentParser("Pi approximation by random sampling")
    ap.add_argument("--seed", "-s", type=int, help="Random seed")
    ap.add_argument(
        "--n_samples",
        "-n",
        type=int,
        default=DEFAULT_N,
        help="Number of samples to draw",
    )
    args = ap.parse_args()
    print(
        f"Running python {sys.argv[0]} "
        f"{' '.join('--' + n + '=' + str(v) for n, v in args.__dict__.items())}",
        file=stderr,
    )
    draws, pi_value = approx_pi(args.seed, args.n_samples)
    result = {
        "pi_value": pi_value,
        "draws": draws,
    }
    with open(OUT_FILE, "w") as f:
        json.dump(result, f, indent=4)


if __name__ == "__main__":
    main()
