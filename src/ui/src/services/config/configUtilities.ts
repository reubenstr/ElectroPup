import { Endpoint, EndpointConfig } from "./configTypes";

export function generateUrl(endpoint: Endpoint): string {
  return `ws://${endpoint.address}:${endpoint.port}`;
}

export function selectedEndpoint(config: EndpointConfig): Endpoint | undefined {
  return config.endpoints[config.selection];
}
