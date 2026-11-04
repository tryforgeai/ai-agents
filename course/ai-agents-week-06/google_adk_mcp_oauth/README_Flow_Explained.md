## The big picture

This project has **two pieces**:

1. **A Python MCP server** that runs a small storefront backend.
2. **A client/agent** that talks to that backend.

The server does two jobs:

1. It hosts transaction features (purchase, view orders, refund).
2. It requires a login before those transactions can run.

Google performs the human login. Your server is the OAuth 2.1 authorization server the MCP client talks to. The client never receives Google's access token.

There is also a public products list. That route does not use MCP and does not require login.

The normative flow is the [MCP authorization specification (2026-07-28)](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization#authorization-flow-steps).

This lab serves the authorization server at `http://localhost:8026`. That is acceptable for a machine-local exercise. A deployment that other machines can reach must serve those endpoints over HTTPS. `localhost` is allowed only for redirect URIs.

---

## KEY TERMS

### MCP

**MCP = Model Context Protocol.** A standard way for a client to call tools hosted on a server.

The MCP tools in this project are:

- `purchase_item` (protected)
- `view_my_orders` (protected)
- `refund_purchase` (protected)

The product list is a normal HTTP route, `GET /products`, not an MCP tool.

### RS

**RS = Resource Server.** The server that hosts the protected resource.

Here the protected resource is `POST /mcp`, which serves the transaction tools. Its canonical URI is `http://localhost:8026/mcp`.

### AS

**AS = Authorization Server.** The server that handles login and issues access tokens to the MCP client.

In this project that authorization server is your own process. It delegates the account login to Google, then issues a separate token for the MCP client.

### OAuth 2.1

OAuth 2.1 is the login-and-permission protocol MCP uses for HTTP transports. This lab uses the authorization-code grant with PKCE (`S256`).

### Two tokens

There are two different access tokens:

| Token | Who holds it | What it is for |
|---|---|---|
| Google access token | Your server only | Calling Google to read `sub`, `email`, and `name` |
| FastMCP JWT | The MCP client | Calling `POST /mcp` |

The JWT's `aud` claim is the MCP resource URL, `http://localhost:8026/mcp`. The client sends it as `Authorization: Bearer <token>`.

### Scope

A scope is a permission. The server puts the scopes it requires in the `401` response. The client requests those scopes. It does not hardcode them.

The default set is:

- `openid`
- `https://www.googleapis.com/auth/userinfo.email`
- `https://www.googleapis.com/auth/userinfo.profile`

### PKCE

PKCE binds the authorization code to the client that started the login. The client sends a `code_challenge` up front and a `code_verifier` when exchanging the code. This lab uses the `S256` method. The server advertises that method in `code_challenge_methods_supported`.

### Client registration

MCP prefers a [Client ID Metadata Document](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/client-registration): an HTTPS URL the client uses as its `client_id`. This lab's agent cannot host that document, so it uses **dynamic client registration** as the fallback. The client registers a localhost callback, and the server accepts only:

- `http://localhost:*`
- `http://127.0.0.1:*`

### Redirect URIs

Two different redirects happen:

- Google sends the browser to your server: `http://localhost:8026/auth/callback`
- Your server then sends the browser to the client's own callback: `http://localhost:<random port>/callback`

### `resource` and `iss`

- `resource` tells the authorization server which MCP server the token is for. The client sends `resource=http://localhost:8026/mcp` on both the authorization request and the token request.
- `iss` is the issuer identifier on the redirect back to the client. The client checks it against the issuer it discovered, as an exact string. `http://localhost:8026` and `http://localhost:8026/` are not the same issuer.

---

## THE FLOW

[MCP authorization flow](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization#authorization-flow-steps)

### Characters

- **You / browser:** where you approve the consent page and log in to Google
- **Client/agent:** ADK agent plus the FastMCP OAuth client
- **Your server:** MCP resource server and the OAuth authorization server
- **Google:** the upstream account login

---

## Step 0: Server starts

The server listens at `http://localhost:8026`.

- Protected MCP endpoint: `POST http://localhost:8026/mcp`
- Public products endpoint: `GET http://localhost:8026/products`

---

## Step 1: Public action — list products

The user asks to list products. The agent calls `GET /products`. The route is public, so the server returns `p1` and `p2` with their prices. No OAuth and no token.

---

## Step 2: Protected action — 401

The user asks to buy, view orders, or refund. The agent calls `POST /mcp` with no token. The server answers **401 Unauthorized** and includes a `WWW-Authenticate` header:

```http
WWW-Authenticate: Bearer resource_metadata="http://localhost:8026/.well-known/oauth-protected-resource/mcp",
                         scope="openid https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"
```

The `scope` value is what the client will request. The `resource_metadata` value is where it discovers the authorization server.

---

## Step 3: Discover the authorization server

The client fetches the protected-resource metadata URL from that header. For this server the path-aware document is:

- `GET /.well-known/oauth-protected-resource/mcp`

That document says the resource is `http://localhost:8026/mcp` and names your process as its authorization server. The client then fetches:

- `GET /.well-known/oauth-authorization-server`

It continues only if `code_challenge_methods_supported` includes `S256`.

---

## Step 4: Register the localhost client

A Client ID Metadata Document is the preferred registration method. This agent has no public HTTPS metadata URL, so it uses dynamic registration.

The client tells your server its callback, for example `http://localhost:54321/callback`, with `application_type` `native`. The server allows the callback only when it matches `http://localhost:*` or `http://127.0.0.1:*`.

---

## Step 5: Start login

The client opens the browser to your server's authorization endpoint. The request includes:

- PKCE `code_challenge` using `S256`
- `state`
- `resource=http://localhost:8026/mcp`
- the scopes from the `401` challenge

---

## Step 6: Consent, then Google

Your server shows its own consent page before sending the browser to Google. Every MCP client shares one Google client id, so this page is the user's chance to see which local client is asking.

After consent, the browser goes to Google. You pick an account and approve the scopes. Google redirects to:

`http://localhost:8026/auth/callback?code=...`

That `code` belongs to the exchange between your server and Google.

---

## Step 7: Your server keeps Google's tokens

Your server exchanges Google's code using `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`. It stores Google's access token. It does not give that token to the MCP client.

It then redirects the browser to the client's localhost callback with a **new** code, the original `state`, and `iss`.

---

## Step 8: The client receives its own token

The client checks `state` and `iss`. It posts the new code to your token endpoint with:

- `code_verifier` (the PKCE secret from step 5)
- the same `resource` value

The token response is a FastMCP JWT. Decode it and look for:

- `iss` equal to the server base URL
- `aud` equal to `http://localhost:8026/mcp`

Google's access token is not inside that JWT.

---

## Step 9: Retry the MCP call

The client calls `POST /mcp` with:

```http
Authorization: Bearer <FastMCP JWT>
```

The server checks the JWT signature, issuer, expiry, and audience. It then uses the stored Google token to read `sub`, `email`, and `name`, and runs the tool for that user.

---
