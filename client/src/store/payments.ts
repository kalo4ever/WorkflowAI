import { produce } from 'immer';
import { create } from 'zustand';
import { client } from '@/lib/api';
import { TenantID } from '@/types/aliases';
import {
  AutomaticPaymentRequest,
  CreatePaymentIntentRequest,
  CustomerCreatedResponse,
  PaymentIntentCreatedResponse,
  PaymentMethodResponse,
} from '@/types/workflowAI';
import { useOrganizationSettings } from './organization_settings';
import { rootTenantPath } from './utils';

interface PaymentsState {
  isLoading: boolean;

  isCreateCustomerInitialized: boolean;
  isPaymentMethodInitialized: boolean;

  stripeCustomerId: string | undefined;
  paymentMethod: PaymentMethodResponse | undefined;

  createCustomer: (tenant: TenantID | undefined) => Promise<void>;
  addPaymentMethod: (tenant: TenantID | undefined, paymentMethodId: string) => Promise<void>;
  getPaymentMethod: (tenant: TenantID | undefined) => Promise<void>;
  createPaymentIntent: (tenant: TenantID | undefined, amount: number) => Promise<PaymentIntentCreatedResponse>;
  updateAutomaticPayment: (
    tenant: TenantID | undefined,
    optIn: boolean,
    threshold: number | null,
    balanceToMaintain: number | null
  ) => Promise<void>;
  deletePaymentMethod: (tenant: TenantID | undefined) => Promise<void>;
}

export const usePayments = create<PaymentsState>((set) => ({
  isLoading: false,

  isCreateCustomerInitialized: false,
  isPaymentMethodInitialized: false,

  stripeCustomerId: undefined,
  paymentMethodId: undefined,
  paymentMethod: undefined,

  createCustomer: async (tenant: TenantID | undefined) => {
    set(
      produce((state: PaymentsState) => {
        state.isLoading = true;
      })
    );
    try {
      const response = await client.post<void, CustomerCreatedResponse>(
        `${rootTenantPath(tenant)}/organization/payments/customers`,
        undefined
      );
      set(
        produce((state: PaymentsState) => {
          state.stripeCustomerId = response.customer_id;
        })
      );
    } catch (error) {
      console.error(error);
    } finally {
      set(
        produce((state: PaymentsState) => {
          state.isLoading = false;
          state.isCreateCustomerInitialized = true;
        })
      );
    }
  },

  getPaymentMethod: async (tenant: TenantID | undefined) => {
    try {
      const response = await client.get<PaymentMethodResponse | null>(
        `${rootTenantPath(tenant)}/organization/payments/payment-methods`
      );
      set(
        produce((state: PaymentsState) => {
          state.paymentMethod = !!response ? response : undefined;
        })
      );
    } catch (error) {
      console.error(error);
    } finally {
      set(
        produce((state: PaymentsState) => {
          state.isPaymentMethodInitialized = true;
        })
      );
    }
  },

  addPaymentMethod: async (tenant: TenantID | undefined, paymentMethodId: string) => {
    set(
      produce((state: PaymentsState) => {
        state.isLoading = true;
      })
    );
    try {
      await client.post<{ payment_method_id: string }, PaymentMethodResponse>(
        `${rootTenantPath(tenant)}/organization/payments/payment-methods`,
        {
          payment_method_id: paymentMethodId,
        }
      );
    } catch (error) {
      throw error;
    } finally {
      set(
        produce((state: PaymentsState) => {
          state.isLoading = false;
          state.isCreateCustomerInitialized = true;
        })
      );
    }

    await usePayments.getState().getPaymentMethod(tenant);
  },

  createPaymentIntent: async (tenant: TenantID | undefined, amount: number) => {
    const response = await client.post<CreatePaymentIntentRequest, PaymentIntentCreatedResponse>(
      `${rootTenantPath(tenant)}/organization/payments/payment-intents`,
      {
        amount,
      }
    );

    return response;
  },

  updateAutomaticPayment: async (
    tenant: TenantID | undefined,
    optIn: boolean,
    threshold: number | null,
    balanceToMaintain: number | null
  ) => {
    try {
      await client.put<AutomaticPaymentRequest>(`${rootTenantPath(tenant)}/organization/payments/automatic-payments`, {
        opt_in: optIn,
        threshold,
        balance_to_maintain: balanceToMaintain,
      });
      await useOrganizationSettings.getState().fetchOrganizationSettings();
    } catch (error) {
      console.error(error);
    }
  },

  deletePaymentMethod: async (tenant: TenantID | undefined) => {
    try {
      await client.del<void>(`${rootTenantPath(tenant)}/organization/payments/payment-methods`);
      await useOrganizationSettings.getState().fetchOrganizationSettings();
      await usePayments.getState().getPaymentMethod(tenant);
    } catch (error) {
      console.error(error);
    }
  },
}));
