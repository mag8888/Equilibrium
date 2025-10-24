import React from 'react';
import styled from 'styled-components';

const PaymentsContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const Title = styled.h1`
  color: white;
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 2rem;
`;

const Payments = () => {
  return (
    <PaymentsContainer>
      <Title>Платежи</Title>
      <p style={{ color: 'rgba(255, 255, 255, 0.8)' }}>
        Платежи в разработке...
      </p>
    </PaymentsContainer>
  );
};

export default Payments;
