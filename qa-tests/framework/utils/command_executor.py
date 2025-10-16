#!/usr/bin/env python3
"""
Command Execution Utilities
Надежное выполнение команд с retry логикой и обработкой ошибок
"""

import subprocess
import time
import logging
from typing import Tuple, Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class CommandResult:
    """Результат выполнения команды"""
    
    def __init__(self, returncode: int, stdout: str, stderr: str, 
                 execution_time: float, command: str):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.execution_time = execution_time
        self.command = command
    
    @property
    def success(self) -> bool:
        """Успешно ли выполнена команда"""
        return self.returncode == 0
    
    @property
    def failed(self) -> bool:
        """Провалилась ли команда"""
        return self.returncode != 0
    
    def __str__(self) -> str:
        return f"CommandResult(code={self.returncode}, time={self.execution_time:.2f}s)"
    
    def __repr__(self) -> str:
        return self.__str__()


class RetryStrategy(Enum):
    """Стратегии повторных попыток"""
    NO_RETRY = "no_retry"
    FIXED_DELAY = "fixed_delay"
    EXPONENTIAL_BACKOFF = "exponential_backoff"


@dataclass
class RetryConfig:
    """Конфигурация повторных попыток"""
    strategy: RetryStrategy = RetryStrategy.FIXED_DELAY
    max_attempts: int = 3
    delay_seconds: float = 1.0
    backoff_multiplier: float = 2.0
    max_delay: float = 30.0


class CommandExecutor:
    """Исполнитель команд с расширенными возможностями"""
    
    def __init__(self, default_timeout: int = 30, 
                 default_retry_config: Optional[RetryConfig] = None):
        self.default_timeout = default_timeout
        self.default_retry_config = default_retry_config or RetryConfig()
        self.logger = logging.getLogger(__name__)
    
    def execute(self, command: str, 
                timeout: Optional[int] = None,
                retry_config: Optional[RetryConfig] = None,
                env: Optional[Dict[str, str]] = None,
                cwd: Optional[str] = None,
                shell: bool = True) -> CommandResult:
        """
        Выполнить команду с retry логикой
        
        Args:
            command: Команда для выполнения
            timeout: Таймаут в секундах
            retry_config: Конфигурация повторных попыток
            env: Переменные окружения
            cwd: Рабочая директория
            shell: Использовать shell
            
        Returns:
            CommandResult: Результат выполнения
        """
        timeout = timeout or self.default_timeout
        retry_config = retry_config or self.default_retry_config
        
        last_result = None
        delay = retry_config.delay_seconds
        
        for attempt in range(retry_config.max_attempts):
            try:
                self.logger.debug(f"Executing command (attempt {attempt + 1}): {command}")
                
                start_time = time.time()
                result = subprocess.run(
                    command,
                    shell=shell,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    env=env,
                    cwd=cwd
                )
                execution_time = time.time() - start_time
                
                last_result = CommandResult(
                    returncode=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    execution_time=execution_time,
                    command=command
                )
                
                # Если команда успешна, возвращаем результат
                if last_result.success:
                    self.logger.debug(f"Command succeeded on attempt {attempt + 1}")
                    return last_result
                
                # Если это последняя попытка, возвращаем результат
                if attempt == retry_config.max_attempts - 1:
                    self.logger.warning(f"Command failed after {retry_config.max_attempts} attempts")
                    return last_result
                
                # Ждем перед следующей попыткой
                if retry_config.strategy != RetryStrategy.NO_RETRY:
                    self.logger.debug(f"Command failed, retrying in {delay}s...")
                    time.sleep(delay)
                    
                    if retry_config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
                        delay = min(delay * retry_config.backoff_multiplier, retry_config.max_delay)
                
            except subprocess.TimeoutExpired:
                execution_time = timeout
                last_result = CommandResult(
                    returncode=-1,
                    stdout="",
                    stderr=f"Command timeout after {timeout}s",
                    execution_time=execution_time,
                    command=command
                )
                
                if attempt == retry_config.max_attempts - 1:
                    self.logger.error(f"Command timed out after {retry_config.max_attempts} attempts")
                    return last_result
                
                self.logger.warning(f"Command timed out, retrying...")
                time.sleep(delay)
                
            except Exception as e:
                execution_time = time.time() - start_time if 'start_time' in locals() else 0
                last_result = CommandResult(
                    returncode=-2,
                    stdout="",
                    stderr=str(e),
                    execution_time=execution_time,
                    command=command
                )
                
                if attempt == retry_config.max_attempts - 1:
                    self.logger.error(f"Command execution failed: {e}")
                    return last_result
                
                self.logger.warning(f"Command execution failed, retrying: {e}")
                time.sleep(delay)
        
        return last_result or CommandResult(-3, "", "Unknown error", 0, command)
    
    def execute_with_validation(self, command: str,
                              expected_returncode: int = 0,
                              expected_stdout_contains: Optional[List[str]] = None,
                              expected_stderr_empty: bool = True,
                              **kwargs) -> CommandResult:
        """
        Выполнить команду с валидацией результата
        
        Args:
            command: Команда для выполнения
            expected_returncode: Ожидаемый код возврата
            expected_stdout_contains: Строки, которые должны быть в stdout
            expected_stderr_empty: Должен ли stderr быть пустым
            **kwargs: Дополнительные параметры для execute()
            
        Returns:
            CommandResult: Результат выполнения
            
        Raises:
            AssertionError: Если результат не соответствует ожиданиям
        """
        result = self.execute(command, **kwargs)
        
        # Проверяем код возврата
        if result.returncode != expected_returncode:
            raise AssertionError(
                f"Expected returncode {expected_returncode}, got {result.returncode}. "
                f"Command: {command}\nStderr: {result.stderr}"
            )
        
        # Проверяем содержимое stdout
        if expected_stdout_contains:
            for expected_text in expected_stdout_contains:
                if expected_text not in result.stdout:
                    raise AssertionError(
                        f"Expected '{expected_text}' in stdout, but not found. "
                        f"Command: {command}\nStdout: {result.stdout}"
                    )
        
        # Проверяем что stderr пустой
        if expected_stderr_empty and result.stderr.strip():
            raise AssertionError(
                f"Expected empty stderr, but got: {result.stderr}. "
                f"Command: {command}"
            )
        
        return result


# Глобальный экземпляр исполнителя команд
default_executor = CommandExecutor()


def execute_command(command: str, **kwargs) -> CommandResult:
    """Удобная функция для выполнения команд"""
    return default_executor.execute(command, **kwargs)


def execute_command_with_validation(command: str, **kwargs) -> CommandResult:
    """Удобная функция для выполнения команд с валидацией"""
    return default_executor.execute_with_validation(command, **kwargs)
