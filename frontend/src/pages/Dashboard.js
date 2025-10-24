import React from 'react';
import { useQuery } from 'react-query';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
  Users, 
  DollarSign, 
  TrendingUp, 
  Award,
  BarChart3,
  CreditCard
} from 'lucide-react';

const DashboardContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  margin-bottom: 2rem;
`;

const Title = styled.h1`
  color: white;
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
`;

const Subtitle = styled.p`
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const StatCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
`;

const StatIcon = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
`;

const StatValue = styled.div`
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
`;

const StatLabel = styled.div`
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
`;

const QuickActions = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
`;

const ActionButton = styled(motion.button)`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 1.5rem;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  
  &:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
  }
`;

const Dashboard = () => {
  const { user } = useAuth();

  const { data: stats, isLoading } = useQuery('dashboard-stats', async () => {
    const response = await api.get('/api/mlm/bonuses/');
    return response.data;
  });

  const quickActions = [
    { icon: Users, label: 'Рефералы', path: '/structure' },
    { icon: BarChart3, label: 'Структура', path: '/structure' },
    { icon: CreditCard, label: 'Платежи', path: '/payments' },
    { icon: Award, label: 'Бонусы', path: '/profile' }
  ];

  return (
    <DashboardContainer>
      <Header>
        <Title>Добро пожаловать, {user?.username}!</Title>
        <Subtitle>Панель управления TRINARY MLM</Subtitle>
      </Header>

      <StatsGrid>
        <StatCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <StatIcon>
            <Users size={24} />
            <StatLabel>Рефералы</StatLabel>
          </StatIcon>
          <StatValue>0</StatValue>
        </StatCard>

        <StatCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <StatIcon>
            <DollarSign size={24} />
            <StatLabel>Заработано</StatLabel>
          </StatIcon>
          <StatValue>$0</StatValue>
        </StatCard>

        <StatCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <StatIcon>
            <TrendingUp size={24} />
            <StatLabel>Ранг</StatLabel>
          </StatIcon>
          <StatValue>Участник</StatValue>
        </StatCard>

        <StatCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <StatIcon>
            <Award size={24} />
            <StatLabel>Статус</StatLabel>
          </StatIcon>
          <StatValue>Активен</StatValue>
        </StatCard>
      </StatsGrid>

      <QuickActions>
        {quickActions.map((action, index) => (
          <ActionButton
            key={action.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 + index * 0.1 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <action.icon size={32} />
            {action.label}
          </ActionButton>
        ))}
      </QuickActions>
    </DashboardContainer>
  );
};

export default Dashboard;
