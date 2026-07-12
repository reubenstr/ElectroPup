import { EndpointConfig } from "./configTypes";

export const defaultEndpoints: EndpointConfig = {
  endpoints: [
    {
      description: "ElectroPup",
      address: "electropup.local",
      port: 80,
    },
    {
      description: "Dev Machine",
      address: "localhost",
      port: 80,
    },
  ],
  selection: 0,
};
