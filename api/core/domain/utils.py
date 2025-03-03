import hashlib


def compute_eval_hash(schema_id: int, input_hash: str, output_hash: str) -> str:
    return hashlib.md5(f"{schema_id}:{input_hash}:{output_hash}".encode()).hexdigest()
