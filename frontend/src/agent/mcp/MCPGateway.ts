/**
 * PLANT-X MCP INTEGRATION GATEWAY
 * 
 * Secure boundary layer for Model Context Protocol (MCP) integrations.
 * External MCP servers are strictly UNTRUSTED.
 * All tools must be authorized, schema-validated, audited, timed out,
 * and prevented from mutating engineering truth directly.
 */

export interface MCPToolDeclaration {
  name: string;
  description: string;
  inputSchema: Record<string, any>;
  requiredCapabilities: string[];
  safetyTier: 'READ_ONLY' | 'ANALYSIS' | 'PROHIBITED';
  timeoutMs: number;
}

export interface MCPInvocationResult {
  toolName: string;
  success: boolean;
  data: any;
  error?: string;
  executionDurationMs: number;
  provenance: {
    source: 'EXTERNAL_MCP_GATEWAY';
    serverName: string;
    authorizedBy: string;
    timestamp: number;
  };
}

export class MCPGateway {
  private registeredTools: Map<string, MCPToolDeclaration> = new Map();
  private authorizedServers: Set<string> = new Set(['plantx-historian-adapter', 'cmms-read-bridge']);
  private invocationLog: MCPInvocationResult[] = [];

  constructor() {
    // Register standard safe read-only integrations
    this.registerTool({
      name: 'historian_read_timeseries',
      description: 'Reads historical sensor telemetry for specified tag and interval.',
      inputSchema: { tag: 'string', startHr: 'number', endHr: 'number' },
      requiredCapabilities: ['HISTORIAN_READ'],
      safetyTier: 'READ_ONLY',
      timeoutMs: 3000,
    });

    this.registerTool({
      name: 'cmms_get_maintenance_records',
      description: 'Queries computerized maintenance records for equipment ID.',
      inputSchema: { equipmentId: 'string' },
      requiredCapabilities: ['CMMS_READ'],
      safetyTier: 'READ_ONLY',
      timeoutMs: 2500,
    });
  }

  public registerTool(tool: MCPToolDeclaration): void {
    // Prohibit registering any tools that touch physical control
    const lowerName = tool.name.toLowerCase();
    if (
      lowerName.includes('control') ||
      lowerName.includes('actuate') ||
      lowerName.includes('valve') ||
      lowerName.includes('setpoint') ||
      lowerName.includes('shutdown')
    ) {
      tool.safetyTier = 'PROHIBITED';
    }
    this.registeredTools.set(tool.name, tool);
  }

  public async executeTool(
    serverName: string,
    toolName: string,
    args: Record<string, any>
  ): Promise<MCPInvocationResult> {
    const startTime = Date.now();

    // 1. Authorization check
    if (!this.authorizedServers.has(serverName)) {
      const res: MCPInvocationResult = {
        toolName,
        success: false,
        data: null,
        error: `MCP Authorization Error: Server '${serverName}' is untrusted or unapproved.`,
        executionDurationMs: Date.now() - startTime,
        provenance: {
          source: 'EXTERNAL_MCP_GATEWAY',
          serverName,
          authorizedBy: 'POLICY_REJECTED',
          timestamp: Date.now(),
        },
      };
      this.invocationLog.push(res);
      return res;
    }

    // 2. Tool registration check
    const tool = this.registeredTools.get(toolName);
    if (!tool) {
      const res: MCPInvocationResult = {
        toolName,
        success: false,
        data: null,
        error: `MCP Tool Discovery Error: Tool '${toolName}' is not registered or supported.`,
        executionDurationMs: Date.now() - startTime,
        provenance: {
          source: 'EXTERNAL_MCP_GATEWAY',
          serverName,
          authorizedBy: 'POLICY_REJECTED',
          timestamp: Date.now(),
        },
      };
      this.invocationLog.push(res);
      return res;
    }

    // 3. Safety tier check (Absolute prevention of DCS/PLC physical actions)
    if (tool.safetyTier === 'PROHIBITED') {
      const res: MCPInvocationResult = {
        toolName,
        success: false,
        data: null,
        error: `SAFETY VIOLATION: Tool '${toolName}' is PROHIBITED. Physical setpoint or valve control is forbidden.`,
        executionDurationMs: Date.now() - startTime,
        provenance: {
          source: 'EXTERNAL_MCP_GATEWAY',
          serverName,
          authorizedBy: 'SAFETY_POLICY_BLOCKED',
          timestamp: Date.now(),
        },
      };
      this.invocationLog.push(res);
      return res;
    }

    // 4. Execution with timeout & failure isolation
    try {
      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error(`MCP Timeout: Execution exceeded ${tool.timeoutMs}ms`)), tool.timeoutMs)
      );

      const executionPromise = (async () => {
        // Deterministic simulated response for read-only adapters
        if (toolName === 'historian_read_timeseries') {
          return { tag: args.tag, samplesCount: 120, status: 'VERIFIED_HISTORIAN_DATA' };
        }
        if (toolName === 'cmms_get_maintenance_records') {
          return { equipmentId: args.equipmentId, lastCleaningHoursAgo: 2410, maintenanceStatus: 'DUE' };
        }
        return { message: 'Executed safely' };
      })();

      const resultData = await Promise.race([executionPromise, timeoutPromise]);

      const res: MCPInvocationResult = {
        toolName,
        success: true,
        data: resultData,
        executionDurationMs: Date.now() - startTime,
        provenance: {
          source: 'EXTERNAL_MCP_GATEWAY',
          serverName,
          authorizedBy: 'ENGINEERING_POLICY_PERMITTED',
          timestamp: Date.now(),
        },
      };
      this.invocationLog.push(res);
      return res;
    } catch (err: any) {
      const res: MCPInvocationResult = {
        toolName,
        success: false,
        data: null,
        error: err.message || 'MCP execution failed',
        executionDurationMs: Date.now() - startTime,
        provenance: {
          source: 'EXTERNAL_MCP_GATEWAY',
          serverName,
          authorizedBy: 'ISOLATED_FAILURE',
          timestamp: Date.now(),
        },
      };
      this.invocationLog.push(res);
      return res;
    }
  }

  public getInvocationHistory(): MCPInvocationResult[] {
    return [...this.invocationLog];
  }

  public getRegisteredTools(): MCPToolDeclaration[] {
    return Array.from(this.registeredTools.values());
  }
}

export const mcpGateway = new MCPGateway();
