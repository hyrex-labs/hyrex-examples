import { HyrexRegistry, getHyrexContext } from '@hyrex/hyrex';

export const workflowRegistry = new HyrexRegistry();

const initiateOnboard = workflowRegistry.task({
    name: 'initiateOnboard',
    config: {
        queue: 'onboarding',
        timeoutSeconds: 30,
    },
    func: async () => {
        const ctx = getHyrexContext();
        console.log(`[${ctx.taskId}] Starting onboarding process`);

        await new Promise(resolve => setTimeout(resolve, 500));

        return {
            onboardingStarted: true,
            timestamp: new Date().toISOString()
        };
    }
});

const validatePayment = workflowRegistry.task({
    name: 'validatePayment',
    config: {
        queue: 'payments',
        timeoutSeconds: 45,
    },
    func: async () => {
        const ctx = getHyrexContext();
        console.log(`[${ctx.taskId}] Validating payment`);

        await new Promise(resolve => setTimeout(resolve, 1000));

        const paymentValid = Math.random() > 0.1;

        return {
            paymentValid,
            paymentMethod: paymentValid ? 'credit_card' : null,
            validatedAt: new Date().toISOString()
        };
    }
});

const validateIdentity = workflowRegistry.task({
    name: 'validateIdentity',
    config: {
        queue: 'identity',
        timeoutSeconds: 60,
    },
    func: async () => {
        const ctx = getHyrexContext();
        console.log(`[${ctx.taskId}] Validating identity`);

        await new Promise(resolve => setTimeout(resolve, 1500));

        const identityScore = Math.floor(Math.random() * 100);

        return {
            identityValid: identityScore > 30,
            identityScore,
            needsCreditCheck: identityScore < 70,
            validatedAt: new Date().toISOString()
        };
    }
});

const validateOrg = workflowRegistry.task({
    name: 'validateOrg',
    config: {
        queue: 'organization',
        timeoutSeconds: 30,
    },
    func: async () => {
        const ctx = getHyrexContext();
        console.log(`[${ctx.taskId}] Validating organization`);

        await new Promise(resolve => setTimeout(resolve, 800));

        const isValidOrg = Math.random() > 0.5;

        return {
            organizationValid: isValidOrg,
            tier: isValidOrg ? 'enterprise' : 'individual',
            validatedAt: new Date().toISOString()
        };
    }
});

const checkCredit = workflowRegistry.task({
    name: 'checkCredit',
    config: {
        queue: 'credit',
        timeoutSeconds: 45,
    },
    func: async () => {
        const ctx = getHyrexContext();

        const needsCreditCheck = Math.random() > 0.3;

        if (!needsCreditCheck) {
            console.log(`[${ctx.taskId}] Credit check skipped`);
            return {
                creditChecked: false,
                creditScore: null,
                creditRating: null,
                checkedAt: null
            };
        }

        console.log(`[${ctx.taskId}] Checking credit`);
        await new Promise(resolve => setTimeout(resolve, 2000));

        const creditScore = Math.floor(Math.random() * 350) + 500;

        return {
            creditChecked: true,
            creditScore,
            creditRating: creditScore > 700 ? 'excellent' : creditScore > 600 ? 'good' : 'fair',
            checkedAt: new Date().toISOString()
        };
    }
});

const trainCreditMachineLearningModel = workflowRegistry.task({
    name: 'trainCreditMachineLearningModel',
    config: {
        queue: 'ml',
        timeoutSeconds: 120,
    },
    func: async () => {
        const ctx = getHyrexContext();

        const hasCreditScore = Math.random() > 0.2;

        if (!hasCreditScore) {
            console.log(`[${ctx.taskId}] No credit score available for training`);
            return {
                modelTrained: false,
                modelVersion: null,
                accuracy: null,
                trainedAt: null
            };
        }

        console.log(`[${ctx.taskId}] Training ML model`);
        await new Promise(resolve => setTimeout(resolve, 3000));

        return {
            modelTrained: true,
            modelVersion: 'v1.2.3',
            accuracy: 0.92,
            trainedAt: new Date().toISOString()
        };
    }
});

const approveUser = workflowRegistry.task({
    name: 'approveUser',
    config: {
        queue: 'approval',
        timeoutSeconds: 30,
    },
    func: async () => {
        const ctx = getHyrexContext();
        console.log(`[${ctx.taskId}] Making approval decision`);

        await new Promise(resolve => setTimeout(resolve, 500));

        const approvalStatus = Math.random() > 0.2 ? 'approved' : 'rejected';

        return {
            approvalStatus,
            reasons: approvalStatus === 'approved' ? ['All validations passed'] : ['Random rejection for demo'],
            tier: 'basic',
            approvedAt: new Date().toISOString()
        };
    }
});

export const onboardUserWorkflow = workflowRegistry.workflow({
    name: 'OnboardUser',
    config: {
        timeoutSeconds: 300,
    },
    body: (workflowBuilder) => {
        workflowBuilder
            .start(initiateOnboard)
            .next([validatePayment, validateIdentity, validateOrg])
            .next(approveUser);

        validateIdentity.next(checkCredit).next(trainCreditMachineLearningModel);

        return workflowBuilder;
    }
});

export {
    initiateOnboard,
    validatePayment,
    validateIdentity,
    validateOrg,
    checkCredit,
    trainCreditMachineLearningModel,
    approveUser
};
