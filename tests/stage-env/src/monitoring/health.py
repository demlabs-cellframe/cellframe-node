"""
Health checking for cellframe nodes.

Provides async health checks using httpx for:
- Node HTTP endpoints
- JSON-RPC endpoints  
- Container health
"""

import asyncio
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

from ..utils.logger import get_logger

logger = get_logger(__name__)


class HealthStatus(BaseModel):
    """Health check result."""
    
    node_id: str
    healthy: bool
    response_time_ms: float
    error: Optional[str] = None
    details: Dict[str, Any] = {}


class HealthChecker:
    """Check health of cellframe nodes."""
    
    def __init__(self, timeout: float = 10.0):
        """
        Initialize health checker.
        
        Args:
            timeout: HTTP request timeout in seconds
        """
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def check_http(self, url: str, node_id: str) -> HealthStatus:
        """
        Check node HTTP endpoint.
        
        Args:
            url: HTTP endpoint URL
            node_id: Node identifier
            
        Returns:
            HealthStatus object
        """
        import time
        
        start = time.time()
        
        try:
            response = await self.client.get(url)
            elapsed_ms = (time.time() - start) * 1000
            
            healthy = response.status_code == 200
            
            logger.debug("http_check",
                        node_id=node_id,
                        status=response.status_code,
                        time_ms=f"{elapsed_ms:.1f}")
            
            return HealthStatus(
                node_id=node_id,
                healthy=healthy,
                response_time_ms=elapsed_ms,
                details={"status_code": response.status_code},
            )
            
        except Exception as e:
            elapsed_ms = (time.time() - start) * 1000
            
            logger.warning("http_check_failed",
                          node_id=node_id,
                          error=str(e))
            
            return HealthStatus(
                node_id=node_id,
                healthy=False,
                response_time_ms=elapsed_ms,
                error=str(e),
            )
    
    async def check_json_rpc(
        self,
        url: str,
        node_id: str,
        method: str = "eth_blockNumber",
    ) -> HealthStatus:
        """
        Check node JSON-RPC endpoint.
        
        Args:
            url: JSON-RPC endpoint URL
            node_id: Node identifier
            method: RPC method to call
            
        Returns:
            HealthStatus object
        """
        import time
        
        start = time.time()
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": [],
            "id": 1,
        }
        
        try:
            response = await self.client.post(url, json=payload)
            elapsed_ms = (time.time() - start) * 1000
            
            data = response.json()
            healthy = "result" in data
            
            logger.debug("rpc_check",
                        node_id=node_id,
                        method=method,
                        healthy=healthy,
                        time_ms=f"{elapsed_ms:.1f}")
            
            return HealthStatus(
                node_id=node_id,
                healthy=healthy,
                response_time_ms=elapsed_ms,
                details={"response": data},
            )
            
        except Exception as e:
            elapsed_ms = (time.time() - start) * 1000
            
            logger.warning("rpc_check_failed",
                          node_id=node_id,
                          error=str(e))
            
            return HealthStatus(
                node_id=node_id,
                healthy=False,
                response_time_ms=elapsed_ms,
                error=str(e),
            )
    
    async def check_multiple(
        self,
        checks: List[tuple[str, str, str]],
    ) -> List[HealthStatus]:
        """
        Check multiple nodes concurrently.
        
        Args:
            checks: List of (url, node_id, check_type) tuples
                   check_type: 'http' or 'rpc'
        
        Returns:
            List of HealthStatus objects
        """
        tasks = []
        
        for url, node_id, check_type in checks:
            if check_type == "http":
                task = self.check_http(url, node_id)
            elif check_type == "rpc":
                task = self.check_json_rpc(url, node_id)
            else:
                raise ValueError(f"Unknown check type: {check_type}")
            
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to HealthStatus
        statuses = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                url, node_id, _ = checks[i]
                statuses.append(HealthStatus(
                    node_id=node_id,
                    healthy=False,
                    response_time_ms=0,
                    error=str(result),
                ))
            else:
                statuses.append(result)
        
        return statuses
    
    async def wait_for_healthy(
        self,
        url: str,
        node_id: str,
        check_type: str = "http",
        timeout: float = 60.0,
        interval: float = 2.0,
    ) -> bool:
        """
        Wait for node to become healthy.
        
        Args:
            url: Endpoint URL
            node_id: Node identifier
            check_type: 'http' or 'rpc'
            timeout: Maximum wait time in seconds
            interval: Check interval in seconds
            
        Returns:
            True if node became healthy, False if timeout
        """
        import time
        
        start = time.time()
        
        while time.time() - start < timeout:
            if check_type == "http":
                status = await self.check_http(url, node_id)
            else:
                status = await self.check_json_rpc(url, node_id)
            
            if status.healthy:
                logger.info("node_healthy",
                           node_id=node_id,
                           wait_time_s=f"{time.time() - start:.1f}")
                return True
            
            await asyncio.sleep(interval)
        
        logger.error("node_health_timeout",
                    node_id=node_id,
                    timeout=timeout)
        return False
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


async def check_nodes_health(
    node_urls: Dict[str, str],
    check_type: str = "http",
) -> Dict[str, HealthStatus]:
    """
    Check health of multiple nodes.
    
    Args:
        node_urls: Dict mapping node_id to URL
        check_type: 'http' or 'rpc'
        
    Returns:
        Dict mapping node_id to HealthStatus
    """
    checker = HealthChecker()
    
    checks = [(url, node_id, check_type) 
              for node_id, url in node_urls.items()]
    
    statuses = await checker.check_multiple(checks)
    
    await checker.close()
    
    return {status.node_id: status for status in statuses}

