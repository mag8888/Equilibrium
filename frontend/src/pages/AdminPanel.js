import React from 'react';
import styled from 'styled-components';

const AdminContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const Title = styled.h1`
  color: white;
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 2rem;
`;

const AdminPanel = () => {
  return (
    <AdminContainer>
      <Title>Админ-панель</Title>
      <p style={{ color: 'rgba(255, 255, 255, 0.8)' }}>
        Админ-панель в разработке...
      </p>
    </AdminContainer>
  );
};

export default AdminPanel;
