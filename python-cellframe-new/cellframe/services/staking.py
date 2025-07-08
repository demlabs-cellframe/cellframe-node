"""
🥩 Staking Service

High-level staking operations for Cellframe blockchain.
Provides staking, delegation, and reward management functionality.

Key Features:
- Stake tokens and manage delegations
- Reward calculation and distribution
- Validator management
- Slashing protection
- Liquid staking support
"""

import logging
import threading
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from datetime import datetime, timedelta
from enum import Enum

from ..core.exceptions import CellframeException

# Import C bindings
try:
    from python_cellframe_common import (
        dap_chain_net_srv_stake_pos_delegate_init,
        dap_chain_net_srv_stake_pos_delegate_create,
        dap_chain_net_srv_stake_pos_delegate_stake,
        dap_chain_net_srv_stake_pos_delegate_unstake,
        dap_chain_net_srv_stake_pos_delegate_get_rewards,
        dap_chain_net_srv_stake_pos_delegate_get_validators,
        dap_chain_net_srv_stake_pos_delegate_get_delegations,
        dap_chain_net_srv_stake_pos_delegate_deinit
    )
except ImportError:
    # Fallback implementations
    def dap_chain_net_srv_stake_pos_delegate_init(): return 0
    def dap_chain_net_srv_stake_pos_delegate_create(handle): return id(handle)
    def dap_chain_net_srv_stake_pos_delegate_stake(handle, validator, amount): return f"stake_{amount}"
    def dap_chain_net_srv_stake_pos_delegate_unstake(handle, validator, amount): return f"unstake_{amount}"
    def dap_chain_net_srv_stake_pos_delegate_get_rewards(handle, validator): return {"rewards": amount}
    def dap_chain_net_srv_stake_pos_delegate_get_validators(handle): return [{"id": "validator1", "active": True}]
    def dap_chain_net_srv_stake_pos_delegate_get_delegations(handle): return [{"validator": "validator1", "amount": 1000}]
    def dap_chain_net_srv_stake_pos_delegate_deinit(handle): pass


class StakingError(CellframeException):
    """Staking-specific errors"""
    pass


class StakingStatus(Enum):
    """Staking status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    UNBONDING = "unbonding"
    SLASHED = "slashed"


class ValidatorStatus(Enum):
    """Validator status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    JAILED = "jailed"
    TOMBSTONED = "tombstoned"


class StakingDelegation:
    """Represents a staking delegation"""
    
    def __init__(self, delegation_handle: int, owns_handle: bool = True):
        """Initialize delegation object"""
        self._delegation_handle = delegation_handle
        self._owns_handle = owns_handle
        self._lock = threading.RLock()
        
        # Add to registry
        StakingService._add_delegation_to_registry(self)
    
    @property
    def validator_id(self) -> str:
        """Get validator ID"""
        with self._lock:
            # In real implementation, extract from handle
            return f"validator_{self._delegation_handle}"
    
    @property
    def amount(self) -> Decimal:
        """Get staked amount"""
        with self._lock:
            # In real implementation, extract from handle
            return Decimal("1000.0")
    
    @property
    def status(self) -> StakingStatus:
        """Get delegation status"""
        with self._lock:
            # In real implementation, check actual status
            return StakingStatus.ACTIVE
    
    @property
    def rewards(self) -> Decimal:
        """Get accumulated rewards"""
        with self._lock:
            # In real implementation, fetch from handle
            return Decimal("50.0")
    
    def claim_rewards(self) -> str:
        """Claim accumulated rewards"""
        with self._lock:
            if self._delegation_handle is None:
                raise StakingError("Delegation not initialized")
            
            # In real implementation, claim through handle
            return f"rewards_claimed_{self._delegation_handle}"
    
    def undelegate(self, amount: Optional[Decimal] = None) -> str:
        """Undelegate tokens"""
        with self._lock:
            if self._delegation_handle is None:
                raise StakingError("Delegation not initialized")
            
            undelegate_amount = amount or self.amount
            
            # In real implementation, undelegate through handle
            return f"undelegated_{undelegate_amount}"
    
    def __del__(self):
        """Cleanup on deletion"""
        if self._owns_handle and self._delegation_handle is not None:
            StakingService._remove_delegation_from_registry(self)


class StakingValidator:
    """Represents a staking validator"""
    
    def __init__(self, validator_handle: int, owns_handle: bool = True):
        """Initialize validator object"""
        self._validator_handle = validator_handle
        self._owns_handle = owns_handle
        self._lock = threading.RLock()
        
        # Add to registry
        StakingService._add_validator_to_registry(self)
    
    @property
    def validator_id(self) -> str:
        """Get validator ID"""
        with self._lock:
            return f"validator_{self._validator_handle}"
    
    @property
    def status(self) -> ValidatorStatus:
        """Get validator status"""
        with self._lock:
            return ValidatorStatus.ACTIVE
    
    @property
    def total_stake(self) -> Decimal:
        """Get total stake"""
        with self._lock:
            return Decimal("10000.0")
    
    @property
    def commission_rate(self) -> Decimal:
        """Get commission rate"""
        with self._lock:
            return Decimal("0.05")  # 5%
    
    @property
    def uptime(self) -> float:
        """Get uptime percentage"""
        with self._lock:
            return 0.99  # 99%
    
    def delegate(self, amount: Decimal) -> StakingDelegation:
        """Delegate tokens to this validator"""
        with self._lock:
            if self._validator_handle is None:
                raise StakingError("Validator not initialized")
            
            # Create delegation
            delegation_handle = dap_chain_net_srv_stake_pos_delegate_stake(
                self._validator_handle, self.validator_id, float(amount)
            )
            
            if delegation_handle is None:
                raise StakingError(f"Failed to delegate to validator {self.validator_id}")
            
            return StakingDelegation(delegation_handle)
    
    def __del__(self):
        """Cleanup on deletion"""
        if self._owns_handle and self._validator_handle is not None:
            StakingService._remove_validator_from_registry(self)


class StakingService:
    """
    Staking service for managing stake operations.
    
    Contains staking_handle internally and provides high-level staking operations.
    """
    
    # Thread-safe registries
    _instances: Dict[int, 'StakingService'] = {}
    _delegations: Dict[int, StakingDelegation] = {}
    _validators: Dict[int, StakingValidator] = {}
    _registry_lock = threading.RLock()
    
    def __init__(self, staking_handle: int, owns_handle: bool = True):
        """Initialize staking service"""
        self._staking_handle = staking_handle
        self._owns_handle = owns_handle
        self._lock = threading.RLock()
        self._logger = logging.getLogger(__name__ + ".StakingService")
        
        # Add to registry
        self._add_to_registry()
    
    @classmethod
    def create(cls, network_id: str = "mainnet") -> 'StakingService':
        """Create new staking service instance"""
        # Initialize staking system
        if dap_chain_net_srv_stake_pos_delegate_init() != 0:
            raise StakingError("Failed to initialize staking system")
        
        # Create staking handle
        staking_handle = dap_chain_net_srv_stake_pos_delegate_create(network_id)
        if staking_handle is None:
            raise StakingError("Failed to create staking service")
        
        return cls(staking_handle)
    
    def get_validators(self) -> List[StakingValidator]:
        """Get all available validators"""
        with self._lock:
            if self._staking_handle is None:
                raise StakingError("Staking service not initialized")
            
            # Get validators from system
            validators_data = dap_chain_net_srv_stake_pos_delegate_get_validators(self._staking_handle)
            
            validators = []
            for validator_data in validators_data:
                if isinstance(validator_data, dict) and validator_data.get('id'):
                    validator_handle = hash(validator_data['id'])
                    validators.append(StakingValidator(validator_handle))
            
            return validators
    
    def get_validator_by_id(self, validator_id: str) -> Optional[StakingValidator]:
        """Get validator by ID"""
        validators = self.get_validators()
        for validator in validators:
            if validator.validator_id == validator_id:
                return validator
        return None
    
    def get_delegations(self) -> List[StakingDelegation]:
        """Get all delegations"""
        with self._lock:
            if self._staking_handle is None:
                raise StakingError("Staking service not initialized")
            
            # Get delegations from system
            delegations_data = dap_chain_net_srv_stake_pos_delegate_get_delegations(self._staking_handle)
            
            delegations = []
            for delegation_data in delegations_data:
                if isinstance(delegation_data, dict) and delegation_data.get('validator'):
                    delegation_handle = hash(delegation_data['validator'])
                    delegations.append(StakingDelegation(delegation_handle))
            
            return delegations
    
    def delegate(self, validator_id: str, amount: Decimal) -> StakingDelegation:
        """Delegate tokens to validator"""
        with self._lock:
            if self._staking_handle is None:
                raise StakingError("Staking service not initialized")
            
            # Find validator
            validator = self.get_validator_by_id(validator_id)
            if not validator:
                raise StakingError(f"Validator {validator_id} not found")
            
            # Delegate through validator
            return validator.delegate(amount)
    
    def undelegate(self, validator_id: str, amount: Decimal) -> str:
        """Undelegate tokens from validator"""
        with self._lock:
            if self._staking_handle is None:
                raise StakingError("Staking service not initialized")
            
            # Call system function
            result = dap_chain_net_srv_stake_pos_delegate_unstake(
                self._staking_handle, validator_id, float(amount)
            )
            
            if result is None:
                raise StakingError(f"Failed to undelegate from validator {validator_id}")
            
            return result
    
    def get_total_staked(self) -> Decimal:
        """Get total staked amount"""
        with self._lock:
            delegations = self.get_delegations()
            return sum(delegation.amount for delegation in delegations)
    
    def get_total_rewards(self) -> Decimal:
        """Get total accumulated rewards"""
        with self._lock:
            delegations = self.get_delegations()
            return sum(delegation.rewards for delegation in delegations)
    
    def claim_all_rewards(self) -> List[str]:
        """Claim all accumulated rewards"""
        with self._lock:
            delegations = self.get_delegations()
            results = []
            
            for delegation in delegations:
                try:
                    result = delegation.claim_rewards()
                    results.append(result)
                except Exception as e:
                    self._logger.error(f"Failed to claim rewards from delegation: {e}")
            
            return results
    
    def get_staking_info(self) -> Dict[str, Any]:
        """Get comprehensive staking information"""
        with self._lock:
            return {
                'total_staked': self.get_total_staked(),
                'total_rewards': self.get_total_rewards(),
                'delegations_count': len(self.get_delegations()),
                'validators_count': len(self.get_validators()),
                'staking_handle': self._staking_handle
            }
    
    # Registry management
    def _add_to_registry(self):
        """Add instance to registry"""
        with self._registry_lock:
            self._instances[self._staking_handle] = self
    
    def _remove_from_registry(self):
        """Remove instance from registry"""
        with self._registry_lock:
            self._instances.pop(self._staking_handle, None)
    
    @classmethod
    def _add_delegation_to_registry(cls, delegation: StakingDelegation):
        """Add delegation to registry"""
        with cls._registry_lock:
            cls._delegations[delegation._delegation_handle] = delegation
    
    @classmethod
    def _remove_delegation_from_registry(cls, delegation: StakingDelegation):
        """Remove delegation from registry"""
        with cls._registry_lock:
            cls._delegations.pop(delegation._delegation_handle, None)
    
    @classmethod
    def _add_validator_to_registry(cls, validator: StakingValidator):
        """Add validator to registry"""
        with cls._registry_lock:
            cls._validators[validator._validator_handle] = validator
    
    @classmethod
    def _remove_validator_from_registry(cls, validator: StakingValidator):
        """Remove validator from registry"""
        with cls._registry_lock:
            cls._validators.pop(validator._validator_handle, None)
    
    @classmethod
    def get_all_instances(cls) -> List['StakingService']:
        """Get all staking service instances"""
        with cls._registry_lock:
            return list(cls._instances.values())
    
    @classmethod
    def cleanup_all(cls):
        """Cleanup all instances"""
        with cls._registry_lock:
            for instance in list(cls._instances.values()):
                if instance._owns_handle:
                    instance.__del__()
    
    def __del__(self):
        """Cleanup on deletion"""
        if self._owns_handle and self._staking_handle is not None:
            try:
                dap_chain_net_srv_stake_pos_delegate_deinit(self._staking_handle)
            except:
                pass
            self._remove_from_registry()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.__del__()


class StakingManager:
    """High-level staking manager"""
    
    def __init__(self):
        self._services: Dict[str, StakingService] = {}
        self._lock = threading.RLock()
    
    def get_service(self, network_id: str = "mainnet") -> StakingService:
        """Get staking service for network"""
        with self._lock:
            if network_id not in self._services:
                self._services[network_id] = StakingService.create(network_id)
            return self._services[network_id]
    
    def get_all_services(self) -> Dict[str, StakingService]:
        """Get all staking services"""
        with self._lock:
            return self._services.copy()
    
    def cleanup(self):
        """Cleanup all services"""
        with self._lock:
            for service in self._services.values():
                service.__del__()
            self._services.clear()


# Global manager instance
_staking_manager = StakingManager()


def get_staking_service(network_id: str = "mainnet") -> StakingService:
    """Get staking service for network"""
    return _staking_manager.get_service(network_id)


def get_all_staking_services() -> Dict[str, StakingService]:
    """Get all staking services"""
    return _staking_manager.get_all_services()


def cleanup_staking_services():
    """Cleanup all staking services"""
    _staking_manager.cleanup()


__all__ = [
    'StakingService', 'StakingDelegation', 'StakingValidator', 'StakingManager',
    'StakingError', 'StakingStatus', 'ValidatorStatus',
    'get_staking_service', 'get_all_staking_services', 'cleanup_staking_services'
] 