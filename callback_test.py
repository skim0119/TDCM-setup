from motors import Motors
from coordinate_navigation import move_to_steps, plot_motor_signal_output
import pigpio
import time
import threading
from motor_signal_detector import PinSignalListener
from motor_advance import Spirob_Motors
import numpy as np
import matplotlib.pyplot as plt
if __name__ == "__main__":     
    print("Start Program")  



    PUL = [17, 25, 22] 
    DIR = [27, 24, 23] 
    MOTOR_ORIENTATION = [True, True, False]
    
    

    start_time = time.time()
    """
    listener = PinSignalListener(PUL)

    listener.listen_to([0,1,2])


    print(listener.pins,listener.being_listened_pins)
    
    listener.start()
    """
    motors = Spirob_Motors(
        PUL, 
        DIR, 
        MOTOR_ORIENTATION,
        steps_per_rev=1600, 
        max_rpm=30, 
        pulse_width=10 * 1e-6,
        debug=False,
        PSL = False, 
        RTSA = False)
        # Caution Method:
        # PSL : Pin Sinagl Listnering, Use pigpio mutilthreading listen to the pin output independently. Don't suggest to use in normal case as it slightly interence the mainloop 
        # RTSA: Enable real_time calculation of the acceleration and speed with linear regressuin for the acuataion driven data flow, its computation time 
                # may greatly affect the motor control signal in the input! Don't suggest to use to get real time data on speed & acctuation 
                # Use real_time_feedback method instead, which sampling feedback on a constant frequency provided by user

    def work():
        move_to_steps(motors,500,1000,1500) #Motor Driven Code
        
    """
    t1 = threading.Thread(target=motors.real_time_feedback, args=())
    t2 = threading.Thread(target=work,args=())
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    """
    motors.real_time_feedback(freq = 20, Animation = False)
    try :
        move_to_steps(motors,500,1000,0)
        move_to_steps(motors,-1100,-2000,1000)

            
    except KeyboardInterrupt:
        print("Main loop interrupted")
    finally:
        motors.pin_listener.plot_pins_signal_output(17) 

        #print(motors.history_collection)
        
        #plot_motor_signal_output(motors.pin_listener.timestamps[25] ,[])
        time = motors.history_collection["Times"]
        x_distance =np.array(motors.history_collection["Distance"])[:,0]
        y_distance =np.array(motors.history_collection["Distance"])[:,1]
        z_distance =np.array(motors.history_collection["Distance"])[:,2]
        
        x_speed =np.array(motors.history_collection["Speed"])[:,0]
        y_speed =np.array(motors.history_collection["Speed"])[:,1]
        z_speed =np.array(motors.history_collection["Speed"])[:,2]
        
        x_acc = np.array(motors.history_collection["Acceleration"])[:,0]
        y_acc = np.array(motors.history_collection["Acceleration"])[:,1]
        z_acc = np.array(motors.history_collection["Acceleration"])[:,2]
        
        
        
        plt.figure(1)

        plt.plot(time,x_distance,color = 'r')
        plt.plot(time,y_distance,color = 'b')
        plt.plot(time,z_distance, color = 'g')
        plt.xlabel("Time")
        plt.ylabel("Distance")
        plt.grid(True)
        plt.tight_layout()
        plt.legend()
        
        
        plt.figure(2)
        
        
        plt.plot(time,x_speed,color = 'r')
        plt.plot(time,y_speed,color = 'b')
        plt.plot(time,z_speed,color = 'g')
        plt.xlabel("Time")
        plt.ylabel("Speed")
        plt.grid(True)
        plt.tight_layout()
        plt.legend()
        
        """
        plt.figure(3)

        plt.plot(time,x_acc)
        plt.plot(time,y_acc)
        plt.plot(time,z_acc)
        plt.xlabel("Time")
        plt.ylabel("Acceleration")
        plt.grid(True)
        plt.tight_layout()
        plt.legend()
        """
        
        def kinetic_post_processing(time,value,distance):
                time = np.array(time)
                value = np.array(value)
                data_pair = np.array([time,value]).T
                for i in range(len(data_pair)):
                        if i >=1:
                                if distance[i] -distance[i-1] ==0:
                                        data_pair = np.delete(data_pair,i)
                                        
                data_pair = data_pair.T
                return data_pair[0], data_pair[1]
        plt.show()
        
       
        
    
