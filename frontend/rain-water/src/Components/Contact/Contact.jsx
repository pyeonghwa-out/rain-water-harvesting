import React from 'react'
import'./contact.css'
import msg_icon from '../../assets/msg1.png'
import mail_icon from '../../assets/msg.png'
import phone_icon from '../../assets/cal.png'
import Location_icon from '../../assets/loc.png'

const Contact = () => {
  return (
    <div className='background'>
    <div className='contact'>
      <div className='contact-col'>
       <div className='header'> <h1 >Contact us</h1> </div>
        <h3>Send us a Message <img src={msg_icon} alt="" /></h3>
        <p>"Feel free to reach out through contact
             form or find our contact information
              below. Your feedback, questions, 
              and suggestions are important to us 
              as we strive to provide exceptional 
              service to our Users
              
              
              
              </p>
              <ul>
                <li><img src={mail_icon} alt="" />rainwater@xyz</li>
                <li><img src={phone_icon} alt="" />+917254xxx</li>
                <li> <img src={Location_icon} alt="" /> Iiit bhagalpurSabour,
                     <br />Bhagalpur, Bihar 813210</li>
              </ul>
      </div>
      <div className='contact-col'>
        <form >
            <label>
                Your name
            </label>
            <input type="text" name='name' placeholder='Enter your name'required />
             <label > Email id </label>
             <input type="tel" name='Phone' placeholder='Enter your Email id' required />
             <label> Write Your message here</label> 
          <textarea name="message" rows="6" placeholder='Enter your message' required></textarea>
          <br />
          <button type='submit' className='btn dark-btn' > Submit now</button>
        </form>
      </div>
       <br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br />
  
    </div>
    </div>
  )
}

export default Contact
