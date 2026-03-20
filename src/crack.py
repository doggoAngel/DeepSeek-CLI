
class antibot:

    def __init__(self, salt: str, expire: int, target: str, difficult: int):
        self.salt = salt
        self.expire = expire
        self.target = target
        self.difficult = difficult
        self.MASK64 = (1 << 64) - 1

        self.RC = [
            0x0000000000000001, 0x0000000000008082, 0x800000000000808A,
            0x8000000080008000, 0x000000000000808B, 0x0000000080000001,
            0x8000000080008081, 0x8000000000008009, 0x000000000000008A,
            0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
            0x000000008000808B, 0x800000000000008B, 0x8000000000008089,
            0x8000000000008003, 0x8000000000008002, 0x8000000000000080,
            0x000000000000800A, 0x800000008000000A, 0x8000000080008081,
            0x8000000000008080, 0x0000000080000001, 0x8000000080008008,
        ]

    def rotl64(self,x, n):
        return ((x << n) | (x >> (64 - n))) & self.MASK64

    def keccak_f1600(self,state_bytes, start_round, end_round):
        s = [int.from_bytes(state_bytes[i*8:(i+1)*8], 'little') for i in range(25)]

        for rnd in range(start_round, end_round):
            C = [s[x] ^ s[x+5] ^ s[x+10] ^ s[x+15] ^ s[x+20] for x in range(5)]
            D = [C[(x+4)%5] ^ self.rotl64(C[(x+1)%5], 1) for x in range(5)]
            for i in range(25):
                s[i] = (s[i] ^ D[i % 5]) & self.MASK64

            t = [0] * 25
            t[0] = s[0]
            t[10] = self.rotl64(s[1], 1);   t[7]  = self.rotl64(s[10], 3)
            t[11] = self.rotl64(s[7], 6);   t[17] = self.rotl64(s[11], 10)
            t[18] = self.rotl64(s[17], 15); t[3]  = self.rotl64(s[18], 21)
            t[5]  = self.rotl64(s[3], 28);  t[16] = self.rotl64(s[5], 36)
            t[8]  = self.rotl64(s[16], 45); t[21] = self.rotl64(s[8], 55)
            t[24] = self.rotl64(s[21], 2);  t[4]  = self.rotl64(s[24], 14)
            t[15] = self.rotl64(s[4], 27);  t[23] = self.rotl64(s[15], 41)
            t[19] = self.rotl64(s[23], 56); t[13] = self.rotl64(s[19], 8)
            t[12] = self.rotl64(s[13], 25); t[2]  = self.rotl64(s[12], 43)
            t[20] = self.rotl64(s[2], 62);  t[14] = self.rotl64(s[20], 18)
            t[22] = self.rotl64(s[14], 39); t[9]  = self.rotl64(s[22], 61)
            t[6]  = self.rotl64(s[9], 20);  t[1]  = self.rotl64(s[6], 44)

            for y in range(0, 25, 5):
                t0, t1, t2, t3, t4 = t[y], t[y+1], t[y+2], t[y+3], t[y+4]
                s[y]   = (t0 ^ ((~t1 & self.MASK64) & t2)) & self.MASK64
                s[y+1] = (t1 ^ ((~t2 & self.MASK64) & t3)) & self.MASK64
                s[y+2] = (t2 ^ ((~t3 & self.MASK64) & t4)) & self.MASK64
                s[y+3] = (t3 ^ ((~t4 & self.MASK64) & t0)) & self.MASK64
                s[y+4] = (t4 ^ ((~t0 & self.MASK64) & t1)) & self.MASK64

            s[0] = (s[0] ^ self.RC[rnd]) & self.MASK64

        out = bytearray(200)
        for i in range(25):
            out[i*8:(i+1)*8] = (s[i] & self.MASK64).to_bytes(8, 'little')
        return bytes(out)


    def deepseek_hash_v1(self, message: bytes) -> str:
        rate = 136
        padlen = rate - (len(message) % rate)
        if padlen == 0:
            padlen = rate
        padded = bytearray(message) + bytearray(padlen)
        padded[len(message)] = 0x06
        padded[-1] |= 0x80

        state = bytearray(200)
        for off in range(0, len(padded), rate):
            for i in range(rate):
                state[i] ^= padded[off + i]
            state = bytearray(self.keccak_f1600(bytes(state), 1, 24))  # round 1..23 (salta round 0)

        return bytes(state[:32]).hex()

    def brute(self) -> int:
        prefix = f"{self.salt}_{self.expire}_"
        for i in range(self.difficult):
            h = self.deepseek_hash_v1((prefix + str(i)).encode())
            if h == self.target:
                return i


