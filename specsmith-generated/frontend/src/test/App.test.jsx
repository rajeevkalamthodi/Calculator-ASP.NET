import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../App.jsx';

function mockFetchOnce(status, body) {
  global.fetch = vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  });
}

describe('CalculadoraWebForms form', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('submits operands and operation and displays the result', async () => {
    mockFetchOnce(200, { result: '5' });
    render(<App />);
    fireEvent.change(screen.getByLabelText('Numero 1'), { target: { value: '2' } });
    fireEvent.change(screen.getByLabelText('Numero 2'), { target: { value: '3' } });
    fireEvent.click(screen.getByText('Somar'));

    await waitFor(() =>
      expect(screen.getByTestId('lbResultado')).toHaveTextContent('5')
    );

    const [, opts] = global.fetch.mock.calls[0];
    const payload = JSON.parse(opts.body);
    expect(payload).toEqual({ operation: 'somar', nro1: '2', nro2: '3' });
  });

  it('sends the selected operation id for divide', async () => {
    mockFetchOnce(200, { result: '2' });
    render(<App />);
    fireEvent.change(screen.getByLabelText('Numero 1'), { target: { value: '6' } });
    fireEvent.change(screen.getByLabelText('Numero 2'), { target: { value: '3' } });
    fireEvent.click(screen.getByText('Dividir'));

    await waitFor(() =>
      expect(screen.getByTestId('lbResultado')).toHaveTextContent('2')
    );
    const payload = JSON.parse(global.fetch.mock.calls[0][1].body);
    expect(payload.operation).toBe('dividir');
  });

  it('shows the error message when the server rejects the input', async () => {
    mockFetchOnce(400, { error: 'Input string was not in a correct format.' });
    render(<App />);
    fireEvent.change(screen.getByLabelText('Numero 1'), { target: { value: 'abc' } });
    fireEvent.click(screen.getByText('Somar'));

    await waitFor(() =>
      expect(screen.getByTestId('error')).toHaveTextContent(
        'Input string was not in a correct format.'
      )
    );
    expect(screen.getByTestId('lbResultado')).toHaveTextContent('');
  });

  it('renders all six operation buttons', () => {
    render(<App />);
    ['Somar', 'Subtrair', 'Multiplicar', 'Dividir', 'Potencia', 'Raiz Quadrada'].forEach(
      (label) => expect(screen.getByText(label)).toBeInTheDocument()
    );
  });
});
