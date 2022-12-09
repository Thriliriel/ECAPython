# vercel.json

[![npm](https://img.shields.io/npm/v/create-vercel.json/latest)](https://www.npmjs.com/package/create-vercel.json)

Quickly scaffold a vercel.json configuration file.

See [vercel.json](src/vercel.json)

## Usage

Using `create-vercel.json` package

```bash
npm create vercel.json
```

Or

Using `vercel.json` package

```bash
npm install -g pnpm
pnpm dlx vercel.json
```

## Known Issues

* The `vercel.json` file is overwritten if it already exists.
* On Windows, `vercel.json` package can be only executed with `pnpm`. See <https://github.com/npm/exec/issues/17>.
