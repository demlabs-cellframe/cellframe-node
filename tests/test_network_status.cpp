#include <gtest/gtest.h>
#include "dap_chain_node_cli_cmd.h" // Предполагаемый заголовочный файл для CLI-команд[](https://gitlab.demlabs.net/cellframe/libdap-chain-net/-/blob/master/dap_chain_node_cli_cmd.h)

// Мок-функция для имитации системного вызова CLI
extern "C" int dap_chain_node_cli_cmd_execute(const char* cmd, char** output);

class NetworkStatusTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Инициализация окружения, если требуется
    }
};

// Тест для проверки команды получения статуса сети
TEST_F(NetworkStatusTest, GetNetworkStatus) {
    char* output = nullptr;
    const char* cmd = "net -net minkowski get status";
    
    // Выполняем команду
    int result = dap_chain_node_cli_cmd_execute(cmd, &output);
    
    // Проверяем, что команда выполнена успешно
    ASSERT_EQ(result, 0) << "Failed to execute network status command";
    
    // Проверяем, что вывод содержит ожидаемую строку
    ASSERT_NE(output, nullptr) << "Output is null";
    std::string output_str(output);
    EXPECT_TRUE(output_str.find("NET_STATE") != std::string::npos) << "Output does not contain network state";
    
    // Освобождаем память
    free(output);
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}