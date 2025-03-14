export class BaseError extends Error {
  capture: boolean;
  extra: Record<string, unknown> | undefined;

  constructor(
    message: string,
    capture: boolean = false,
    extra: Record<string, unknown> | undefined = undefined
  ) {
    super(message);

    this.capture = capture;
    this.extra = extra;
  }
}

export class StreamError extends BaseError {}
