#include <cstring>
extern "C" {
    #include <dap_enc_base58.h>
}

#include <gtest/gtest.h>

TEST(Base58, Roundtrip32) {
    uint8_t src[32];
    for (size_t i = 0; i < sizeof(src); ++i) src[i] = static_cast<uint8_t>(i);

    char *encoded = nullptr;
    int enc_len = dap_enc_base58_encode(src, sizeof(src), &encoded);
    ASSERT_GT(enc_len, 0) << "Encoding failed";

    uint8_t dst[32];
    size_t dst_len = 0;
    bool ok = dap_enc_base58_decode(encoded, dst, &dst_len);

    EXPECT_TRUE(ok);
    EXPECT_EQ(dst_len, sizeof(src));
    EXPECT_EQ(std::memcmp(src, dst, sizeof(src)), 0);

    free(encoded);
}
