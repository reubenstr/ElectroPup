export type Endpoint = {
  description: string;
  address: string;
  port: number;
};

export type EndpointConfig = {
  endpoints: Endpoint[];
  selection: number;
};
