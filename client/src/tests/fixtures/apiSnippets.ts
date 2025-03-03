import {
  CodeLanguage,
  InstallInstruction,
  InstallationSnippet,
} from '@/types/snippets';

export const apiSnippetsFixture: InstallationSnippet = {
  [InstallInstruction.SDK]: {
    language: CodeLanguage.BASH,
    code: 'npm install workflowai',
  },
  [InstallInstruction.INSTALL]: {
    language: CodeLanguage.TYPESCRIPT,
    code: `
const parsers: Record<string, (val: any) => any> = {
  $oid: (value: string) => value,
  $date: parseDate,
  $numberLong: (value: string) => parseInt(value, 10),
  $numberInt: (value: string) => parseInt(value, 10),
  $numberDouble: (value: string) => parseFloat(value),
  $binary: (value: { base64: string; subType: string }) => value.base64,
};

export function ejsontoPlainJS<T>(obj: unknown): T {
  if (!obj || typeof obj !== 'object') {
    return obj as T;
  }
  if (Array.isArray(obj)) {
    return obj.map(ejsontoPlainJS) as T;
  }

  const keys = Object.keys(obj);
  if (keys.length === 1 && keys[0] in parsers) {
    const key = keys[0];
    const parser = parsers[key];
    // @ts-expect-error key is in parsers
    return parser(obj[key]);
  }

  return Object.entries(obj).reduce(
    (acc, [k, v]) => ({
      ...acc,
      [k]: ejsontoPlainJS(v),
    }),
    {} as T
  );
}
    `,
  },
  [InstallInstruction.RUN]: {
    language: CodeLanguage.PYTHON,
    code: `
import math
import time
from typing import TypeVar

import httpx
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.ec import (
    ECDSA,
    SECP256R1,
    EllipticCurvePublicKey,
    EllipticCurvePublicNumbers,
)
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
from pydantic import BaseModel

from core.utils.strings import b64_urldecode


class JWK(BaseModel):
    kty: str
    x: str
    y: str
    crv: str
    id: str

    def public_key(self) -> EllipticCurvePublicKey:
        x_bytes = b64_urldecode(self.x)
        y_bytes = b64_urldecode(self.y)

        x_int = int.from_bytes(x_bytes, "big")
        y_int = int.from_bytes(y_bytes, "big")

        if self.crv != "P-256" or self.kty != "EC":
            raise AssertionError("Only P-256 is supported")

        # TODO: support other curves
        public_numbers = EllipticCurvePublicNumbers(x_int, y_int, SECP256R1())
        return public_numbers.public_key(default_backend())
    `,
  },
};
