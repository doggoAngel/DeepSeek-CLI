# DeepSeek CLI 

This is a CLI that uses the web chat API of DeepSeek.  
This means you can create your own custom projects with Deepseek model without purchasing API tokens.

To block this, Deepseek develepers implement a security layer — a hash challenge required for all API calls.  
I performed reverse engineering on this challenge and also created a Python library for it.

Check the video demo:  

VIDEO

## Topics
    1. Reverse Engineering  
    2. Simple CLI
    3. Python library


## 1. Revere Engineering 

First thing i did, setup my burpsuite and the browser to see all traffic that send to the server. And i see that all request have a custom Header called: X-Ds-Pow-Response that contians a json encode in base64:

![alt text](pic/SCR-20260319-jiwx.png)

```json
{
    "algorithm":"DeepSeekHashV1",
    "challenge":"0e0bedaf8208eb2eaac0c7ff4ed6240c583fc0b0206a15f6a9cfd9fcd783a5e4",
    "salt":"5e7de0aa2ded76976ecc",
    "answer":120159,"signature":"5ce10c31b8ca477528013c3695ee1ec04f83f79185e8161b37c9770545352a23",
    "target_path":"/api/v0/chat/completion"
}
```
This json contains:

- The name of alghoritm: "DeepSeekHashV1".
- The target HASH called challenge.
- The salt of HASH.
- The answer of challenge.
- The signature.
- The target path, in this case is use to send message into the chat.

To take that challenge, the client need to do a call to: POST /api/v0/chat/create_pow_challenge before all api calls, in side the body there is a json with: target_path that contians the path of the second call.

![alt text](pic/SCR-20260319-jote.png)

To resolve this challenge the alghoritm need these (this information i know after the analisys of main.js and wasm compilate):

1. The target HASH: "challenge":"8eaf30a1390670ffc55123b7d01214164fc18491f946f69d1ea78f8912f663bc".
2. The salf: "salt":"8c7c7d75efa43eb22d2a".
3. The difficulty: "difficulty":144000.
4. The expire at: "expire_at":1773855887108.

### Analisys of main.ddb03f9fed.js

After searching this string: pow and start the debbuger, i notizie that the calculation of hash is execute by Wrokers (is a parallel thread separte of father thread), syntax: 

```javascript
let w = new Worker("file.js");
```
The Worker exec the code inside file.js. To comunicate to the worker use this method:

```javascript
w.postMessage("start');
```
in side the file.js there is function that take that message and elaborate... but in this article i dont want explain javascript, so let go with Reverse Engineering.

So, in main.ddb03f9fed.js there are two Workers:

```javascript
//******some code*******
//This is the worker that we need to analize
let t = new Worker(new URL(n.p + n.u("33614"), n.b), Object.assign({},{type:"module"},{type: void 0}))

//*******some code*******
let t1 = new Worker(new URL(n.p + n.u("38401"), n.b), Object.assign({},{type:"module"},{type: void 0}))
```

I searched in the main file the two IDS and n.u, and i found values:

    Key: 33614 Value: "1ba98674d4"
    key: 38401 Value: "a8c4129551"

I searched also n.p and it contains a link:

    https://fe-static.deeepseek.com/chat

The final URL is(for id 33614):

    https://fe-static.deeepseek.com/chat/static/33614.1ba98674d4.js

### Analisy of 33614 JS

In the main js, there is this code:

```javascript
t.postMessage({
    type: "pow-challenge",
    challenge: e
})
```
The variable e contain the json (HASH, salt, expire_at ....)

Inside the onmessage, there is a concatenation of string:

```text
<salt value> + "_" + <expire at value> + "_"
```
That is start of string hash to calculate, piu' avanti.

after the concatenation, the js call a functon saved into a WASM file, this wasm file was wrote in RUST.
That function is called: 

```javascript
n.wasm_solve(<base address>, <start hash address>, <lengh of hash>, <start concatention adress>, <lenght of concatenation>, <difficulty>)
```

So, i donwload the file wasm.

### Analisys of WASM file

To decompilate and analisys a file wasm in Ghidra, we need to install this plugin.zip in releases: 

    https://github.com/nneonneo/ghidra-wasm-plugin

After installing ghidra is able to decompilate the file WASM.

![alt text](pic/SCR-20260319-kpax.png)
