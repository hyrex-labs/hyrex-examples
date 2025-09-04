'use server';

import { helloWorldTask } from '../../hyrex/tasks';
import { OnboardUserWorkflow } from '../../hyrex/workflows';

export async function triggerHelloWorld(name?: string) {
  try {
    const taskId = await helloWorldTask.send({ name: name || 'World' });

    return {
      success: true,
      message: `Task submitted for ${name || 'World'}`,
      taskId
    };
  } catch (error) {
    console.error('Error triggering hello world task:', error);
    return {
      success: false,
      error: 'Failed to trigger task'
    };
  }
}

export async function triggerUserOnboarding() {
  try {
    const workflowId = await OnboardUserWorkflow.send();

    return {
      success: true,
      message: `User onboarding workflow started`,
      workflowId
    };
  } catch (error) {
    console.error('Error triggering user onboarding workflow:', error);
    return {
      success: false,
      error: 'Failed to trigger onboarding workflow'
    };
  }
}
