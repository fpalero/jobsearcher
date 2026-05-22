export interface Job {
  id: number;
  jobId: string;
  company: string;
  title: string;
  location: string;
  salary: string;
  matchPercentage: number;
  logoUrl: string;
  description: string;
  tags: string[];
  postedDate: string;
  applicable?: boolean;
  applyLink?: string;
  saved?: boolean;
  applied?: boolean;
  responsibilities?: string[];
  requirements?: string[];
  feedback?: 'positive' | 'negative' | null;
}

export const MOCK_JOBS: Job[] = [
  {
    id: 1,
    jobId: 'mock-001',
    company: 'Velocity AI',
    title: 'Senior Frontend Engineer',
    location: 'San Francisco, CA (Remote)',
    salary: '$160k – $210k',
    matchPercentage: 95,
    logoUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAHwpl6hfLW5hehIVNDcMGgOEyfGkNqWlZ56aF3M6DP37bs5-I9btNvlxZwVqtzD1VYz5i6XFwbJgefAc3Pg9C9CL85qSRn3aEUWHRcjhoqnqEh94r69DeoceRpsZ_R-GToQ9F4WB4vBE0tLG2vL1CsjbY76PT2d1u6iaizMEcQg6sVYQilnMB_-6q2ou441bShYWF8WljA8vpXORJ7_rSaRfHFkWf-SmQYQn_ipwO578T2rt3CGt3KceXC7y1m-w3WR1E-ypPDFp0',
    description: "We're looking for a React expert to lead our core interface team. You will be responsible for architecting high-performance visualization components for our generative AI platform, ensuring accessibility and seamless user interactions.",
    tags: ['React', 'TypeScript', 'Next.js', 'Tailwind CSS'],
    postedDate: '2 days ago',
  },
  {
    id: 2,
    jobId: 'mock-002',
    company: 'Lumina Finance',
    title: 'Frontend Architect',
    location: 'New York, NY',
    salary: '$190k – $240k',
    matchPercentage: 80,
    logoUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCa203fplO4gMQb5ThckoE2moth6Bo2bfpLa05ypCjO2kc5XSda0j_deOzupChBWW1qE12UVAK6WH0eq1Ulz46Q87ib6XEn3P7-8gtBAFJM0pwSV4C4MpLVFf9DOeU7lK_i1h1_CUkG4aCeHKYAp7rP0gqjn0_LK7z6-4fmfCBpfVOxbKU_eDFJ11rtcwHueIuitwomqPGJ9P4uAsch9ZRxnp_VSKLMPoRREw8qClnPJPbLV5sMEB_Cbcu4TDCMrQi_aJWgPoa8S0I',
    description: 'Lead the digital transformation of our flagship banking application. We need a visionary who can balance cutting-edge technology with the strict security requirements of a global financial leader.',
    tags: ['Vue.js', 'D3.js', 'WebAssembly'],
    postedDate: '1 week ago',
  },
  {
    id: 3,
    jobId: 'mock-003',
    company: 'EcoSphere',
    title: 'UI/UX Developer',
    location: 'Austin, TX',
    salary: '$140k – $180k',
    matchPercentage: 92,
    logoUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuA-UilOMuwwu6XorC1gB7ZXN4OcF6hWG5LjN4L3BG-tfzm4GbAzwq_IY9iT96XeJfaMg4921lYssBsq_otB8f2RspD_IoHwuOukPqvzYd2LJ_sUVT7sDA0bS8QVWYBW58NJm8YWpf5bZZGdcBX_CPBb6qYGbGvL9_2RLTwNy7frbuadkXsjFoUq4ijfrZNoeKdx9HmwYBJogOfbgOLjUgpktj7vJ6kWdM23OP-5eAKZCZV9EvX8eu3Zd-3D9diXrvnQcm813tV4j5g',
    description: "Join our missions to fight climate change. We're building the first consumer-facing carbon tracking dashboard and need a developer who cares as much about user delight as they do about clean code.",
    tags: ['React Native', 'Framer Motion', 'Node.js'],
    postedDate: '3 days ago',
  },
  {
    id: 4,
    jobId: 'mock-004',
    company: 'QuantumFlow Systems',
    title: 'Senior Frontend Engineer',
    location: 'Remote (San Francisco, CA)',
    salary: '$160k – $220k',
    matchPercentage: 95,
    logoUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCE6bksGFjSGlKH7q2GYyhVDdH-QIxoGL9ZyXj6KUT_09Vi6BHAzSnUuPyXd8O-kQWv0yRCFA45hCEe4z0CSGhRa7IMxCKjV9gTJULz0u-o679yyQqZ_HJWhbFaT4A-9EDrusunyYfvosd4EQ_HJFyr1BVWSh5HtDsxrUtQv7ej7rDezsy08oDnKSd5_tFCCU9wZGZKMAUs-dw4SrSbE2dIk628-ugnwubfHglLSRbcdP-PZCCV8FUmzmUZj4D5RP5P0ECEbN_qvrg',
    description: 'QuantumFlow Systems is building the next generation of real-time data visualization platforms for enterprise logistics. We are seeking a Senior Frontend Engineer who is passionate about building high-performance, accessible, and beautiful user interfaces.',
    tags: ['React', 'TypeScript', 'Next.js', 'D3.js'],
    postedDate: '2 days ago',
  },
];
