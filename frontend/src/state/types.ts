export interface Node {
  user: string;
  parent: string | null;
  position: number;
  level: number;
  tariff: string | null;
  children: Node[];
}

export interface QueueEntry {
  id: number;
  user: number;
  user_display: string;
  amount: string;
  inviter: string | null;
  tariff: {
    code: string;
    name: string;
    entry_amount: string;
  };
}
