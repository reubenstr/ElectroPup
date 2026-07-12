import { EndpointConfig } from "./configTypes";

export const defaultEndpoints: EndpointConfig = {
  endpoints: [
    {
      description: "ElectroPup",
      address: "electropup.local",
      port: 80,
    },
    {
      description: "Local Machine",
      address: "localhost",
      port: 80,
    },
    {
      description: "Remote Machine",
      address: "192.168.1.143",
      port: 80,
    },
  ],
  selection: 0,
};
