
export enum ServerType {
    HEXAPOD
}

export interface Endpoint {
    description: string;
    address: string;
    port: number;
    encrypted: boolean;
}

export interface Server {
    type: ServerType,
    name: string,
    endpoints: Endpoint[],
    selectedEndpoint: Endpoint;
}

