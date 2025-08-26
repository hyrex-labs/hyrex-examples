'use server';

import { helloWorldTask } from '../../hyrex/app';

export async function triggerHelloWorld(name?: string) {
  try {
    const result = await helloWorldTask.send({ name: name || 'World' });
    
    return { 
      success: true, 
      message: `Task submitted for ${name || 'World'}`,
      taskId: result.id 
    };
  } catch (error) {
    console.error('Error triggering hello world task:', error);
    return { 
      success: false, 
      error: 'Failed to trigger task' 
    };
  }
}